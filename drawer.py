from asyncio import AbstractEventLoop, new_event_loop, sleep
from os import getenv
from time import time

# from keyboard import add_hotkey # keyboard requires root but playwright doesn't run with root so i switched to pynput
from playwright.async_api import Locator, Page, Playwright
from playwright_localstorage import AsyncLocalStorageAccessor
from pynput.keyboard import Key, KeyCode, Listener

loop = new_event_loop()


class Drawer:
    game_url: str
    loading_url: str
    keys: set[Key | KeyCode]
    sync_delay: float = 0.1

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

        self.game_browser = await self.playwright.firefox.launch(headless=True)
        self.game_page: Page | None = None
        self.game_canvas: Locator | None = None

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
            """async (element, src) => {
                img = new Image();
                img.src = src;
                await img.decode();
                element.getContext("2d").drawImage(img, 0, 0, element.width, element.height);
            }""",
            await self.game_canvas.evaluate(
                "(element, quality) => element.toDataURL('image/jpeg', quality)",
                self.quality
            )
        )

    def _on_key_press(self, key: Key | KeyCode):
        if key not in self.keys:
            return

        pass  # override this

    def _on_key_release(self, key: Key | KeyCode):
        if key not in self.keys:
            return

        pass  # override this

    async def _print_fps(self, frames: list[float | int]):
        print(f"\r{round(len(frames) / 10, 2)} fps        ", end="")

    async def start_listeners(self):
        print("\rstart listeners      ", end="")
        Listener(on_press=self._on_key_press, on_release=self._on_key_release).start()

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
