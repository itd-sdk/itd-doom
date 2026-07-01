from asyncio import AbstractEventLoop, new_event_loop, run_coroutine_threadsafe, sleep
from os import getenv
from time import time

# from keyboard import add_hotkey # keyboard requires root but playwright doesn't run with root so i switched to pynput
from playwright.async_api import FloatRect, Locator, Page, Playwright
from playwright_localstorage import AsyncLocalStorageAccessor
from pynput.keyboard import Key, KeyCode
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Controller
from pynput.mouse import Listener as MouseListener

loop = new_event_loop()

keymap: dict[Key, str] = {
    Key.ctrl: "Control",
    Key.alt: "Alt",
    Key.shift: "Shift",
    Key.space: "Space"
}


class Drawer:
    game_url: str
    loading_url: str
    sync_delay: float = 0.1
    mouse = False
    lock_mouse = False
    _get_image_script = "(element, quality) => element.toDataURL('image/jpeg', quality)"

    async def __init__(
        self, p: Playwright, loop: AbstractEventLoop, quality: float = 0.5
    ):
        print("\rinit", end="")

        self.playwright = p
        self.loop = loop
        self.quality = quality

        self.itd_browser = await self.playwright.firefox.launch(headless=False)
        self.itd_context = await self.itd_browser.new_context()
        self.itd_page: Page | None = None
        self.itd_canvas: Locator | None = None
        self.itd_bounding_box: FloatRect | None = None
        self.game_bounding_box: FloatRect | None = None

        self.game_browser = await self.playwright.firefox.launch(headless=True)
        self.game_page: Page | None = None
        self.game_canvas: Locator | None = None

        self._mouse_controller = Controller()
        self.center_x = 0
        self.center_y = 0
        self._mouse_pos = (0, 0)

    async def open_itd(self):
        print("\ropen itd       ", end="")
        await self.itd_context.add_cookies(
            [
                {
                    "name": "refresh_token",
                    "value": getenv("TOKEN", ""),
                    "domain": ".xn--d1ah4a.com",
                    "path": "/api/v1/auth",
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "Lax"
                },
                {
                    "name": "is_auth",
                    "value": "1",
                    "domain": ".xn--d1ah4a.com",
                    "path": "/",
                    "secure": True
                }
            ]
        )

        self.itd_page = await self.itd_context.new_page()
        await self.itd_page.goto("https://xn--d1ah4a.com/")

        accessor = AsyncLocalStorageAccessor(self.itd_page)
        await accessor.set("seen_announcements", '["new-feed-2026-06-15"]')
        await self.itd_page.reload()

        await self.itd_page.get_by_title("Нарисовать").click()
        self.itd_canvas = self.itd_page.locator("canvas")

    async def open_game(self):
        print("\ropen game     ", end="")
        self.game_page = await self.game_browser.new_page()
        await self.game_page.goto(self.game_url)
        self.game_canvas = self.game_page.locator("canvas").last

    async def init_itd_canvas(self):
        assert self.itd_canvas
        assert self.itd_page
        print("\rinit canvas       ", end="")

        await self.itd_canvas.evaluate(
            "(element) => {element.parentNode.appendChild(element.cloneNode(true)); element.remove()}"  # remove all event listeners (to user cant draw)
        )
        await self.itd_canvas.evaluate(
            """async (element, src) => {
                img = new Image();
                img.src = src;
                await img.decode();
                element.getContext("2d").drawImage(img, 0, 0, element.width, element.height);
            }""",
            self.loading_url
        )

        await self.itd_page.wait_for_timeout(2000)

    async def sync_canvas(self):
        assert self.itd_canvas
        assert self.game_canvas
        await self.itd_canvas.evaluate(
            """async (element, data) => {
                img = new Image();
                img.src = data[0];
                await img.decode();
                context = element.getContext("2d");
                context.drawImage(img, 0, 0, element.width, element.height);
                context.fillStyle = "white";
                //context.fillRect(data[1], data[2], 10, 10);
            }""",
            (
                await self.game_canvas.evaluate(self._get_image_script, self.quality),
                *self._mouse_pos
            )
        )

    def _on_key_press(self, key: Key | KeyCode):
        assert self.game_page
        if isinstance(key, KeyCode):
            run_coroutine_threadsafe(self.game_page.keyboard.down(key.char), self.loop)
        elif key in keymap:
            run_coroutine_threadsafe(
                self.game_page.keyboard.down(keymap[key]), self.loop
            )

    def _on_key_release(self, key: Key | KeyCode):
        assert self.game_page
        if isinstance(key, KeyCode):
            run_coroutine_threadsafe(self.game_page.keyboard.up(key.char), self.loop)
        elif key in keymap:
            run_coroutine_threadsafe(self.game_page.keyboard.up(keymap[key]), self.loop)

    def _on_mouse_move(self, x: int, y: int, wait: bool = False):
        assert self.itd_canvas
        assert self.game_page
        assert self.game_canvas

        if self.center_x == 0 and self.center_y == 0:
            self.center_x, self.center_y = x, y
            return

        if self.itd_bounding_box is None:
            self.itd_bounding_box = run_coroutine_threadsafe(
                self.itd_canvas.bounding_box(), self.loop
            ).result()
            if self.itd_bounding_box is None:
                print("!! box is none")
                return

        if self.game_bounding_box is None:
            self.game_bounding_box = run_coroutine_threadsafe(
                self.game_canvas.bounding_box(), self.loop
            ).result()
            if self.game_bounding_box is None:
                print("!! box is none")
                return

        if self.lock_mouse:
            if self.center_x == x and self.center_y == y:
                return

            # я не знаю почему 135 и почему itd_bounding_box["width"], но это работает
            # 135 я вручную посчитал (если больше то мышка уходит всегда вверх, есили меньше то всегда вниз). на других компах мб другое значение
            run_coroutine_threadsafe(
                self.game_page.mouse.move(
                    (self.itd_bounding_box["x"] + self.itd_bounding_box["width"] / 2)
                    + (x - self.center_x),
                    (self.itd_bounding_box["height"] / 2) + 135 + (y - self.center_y)
                ),
                self.loop
            )
            self._mouse_controller.position = (self.center_x, self.center_y)
        else:
            self._mouse_pos = (
                self.game_bounding_box["x"]
                + (x - self.center_x + self.itd_bounding_box["width"] / 2)
                * (self.game_bounding_box["width"] / self.itd_bounding_box["width"]),
                self.game_bounding_box["y"]
                + (y - self.center_y + self.itd_bounding_box["height"] / 2)
                * (self.game_bounding_box["height"] / self.itd_bounding_box["height"])
            )
            future = run_coroutine_threadsafe(
                self.game_page.mouse.move(*self._mouse_pos), self.loop
            )
            if wait:
                future.result()

    def _on_mouse_click(self, x: int, y: int, button: str, pressed: bool):
        assert self.game_page

        self._on_mouse_move(x, y, wait=not self.lock_mouse)
        if pressed:
            run_coroutine_threadsafe(self.game_page.mouse.down(), self.loop).result()
        else:
            run_coroutine_threadsafe(self.game_page.mouse.up(), self.loop).result()

    async def _print_fps(self, frames: list[float | int]):
        print(f"\r{round(len(frames) / 10, 2)} fps        ", end="")

    async def start_listeners(self):
        print("\rstart listeners      ", end="")
        KeyboardListener(
            on_press=self._on_key_press, on_release=self._on_key_release
        ).start()
        print(self.mouse)
        if self.mouse:
            MouseListener(
                on_move=self._on_mouse_move, on_click=self._on_mouse_click
            ).start()

    async def run_syncing(self):
        frames: list[float | int] = []
        while True:
            await self.sync_canvas()
            await sleep(self.sync_delay)
            frames.append(time())
            frames = [f for f in frames if f > time() - 10]
            await self._print_fps(frames)

    async def run(self):
        await self.open_itd()
        await self.init_itd_canvas()

        await self.open_game()
        await self.start_listeners()
        await self.run_syncing()
