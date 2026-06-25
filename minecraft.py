from asyncio import run_coroutine_threadsafe

from pynput.keyboard import Key, KeyCode
from pynput.mouse import Controller, Listener

from drawer import Drawer


class MinecraftDrawer(Drawer):
    game_url = "https://mcraft.fun/"
    loading_url = (
        "https://cdn.xn--d1ah4a.com/images/2efc31b0-87b3-4844-b9e5-54be74168623.jpg"
    )
    keys = (
        KeyCode.from_char("w"),
        KeyCode.from_char("a"),
        KeyCode.from_char("s"),
        KeyCode.from_char("d"),
        Key.space
    )

    async def __init__(self, p, loop, quality: float = 0.5):
        await super().__init__(p, loop, quality)
        self._mouse_controller = Controller()
        self.center_x = 0
        self.center_y = 0

    def _on_key_press(self, key: Key | KeyCode):
        assert self.game_page
        if isinstance(key, KeyCode):
            run_coroutine_threadsafe(self.game_page.keyboard.down(key.char), self.loop)
        elif key == Key.space:
            run_coroutine_threadsafe(self.game_page.keyboard.down("Space"), self.loop)

    def _on_key_release(self, key: Key | KeyCode):
        assert self.game_page
        if isinstance(key, KeyCode):
            run_coroutine_threadsafe(self.game_page.keyboard.up(key.char), self.loop)
        elif key == Key.space:
            run_coroutine_threadsafe(self.game_page.keyboard.up("Space"), self.loop)

    def _on_mouse_move(self, x: int, y: int):
        assert self.game_page
        if self.center_x == 0 and self.center_y == 0:
            self.center_x, self.center_y = x, y
            return
        if self.center_x == x and self.center_y == y:
            return

        box = run_coroutine_threadsafe(
            self.game_page.locator("body").bounding_box(), self.loop
        ).result()
        if box is None:
            print("!! box is none")
            return
        run_coroutine_threadsafe(
            self.game_page.mouse.move(
                (box["x"] + box["width"] / 2) + (x - self.center_x),
                (box["y"] + box["height"] / 2) + (y - self.center_y)
            ),
            self.loop
        )

        self._mouse_controller.move(
            self.center_x - self._mouse_controller.position[0],
            self.center_y - self._mouse_controller.position[1]
        )
        print(f"move {x} {y}")

    def _on_mouse_click(self, x: int, y: int, button: str, pressed: bool):
        assert self.game_page

        box = run_coroutine_threadsafe(
            self.game_page.locator("body").bounding_box(), self.loop
        ).result()
        if box is None:
            print("!! box is none")
            return

        print("click")
        run_coroutine_threadsafe(
            self.game_page.mouse.click(
                (box["x"] + box["width"] / 2) + (x - self.center_x),
                (box["y"] + box["height"] / 2) + (y - self.center_y)
            ),
            self.loop
        )

    async def start_listeners(self):
        await super().start_listeners()
        Listener(on_move=self._on_mouse_move, on_click=self._on_mouse_click).start()

        assert self.itd_page
        await self.itd_page.evaluate(
            "document.addEventListener('mousemove', event => {window.pageX = event.clientX; window.pageY = event.clientY})"
        )

    async def open_game(self):
        await super().open_game()
        assert self.game_page
        await self.game_page.get_by_text("Singleplayer").click()
        await self.game_page.get_by_text("Create New World").click()
        await self.game_page.get_by_placeholder("World name").type(
            "itd-drawer world (by itd-sdk) 676767766767"
        )
        await self.game_page.get_by_text("Create", exact=True).click()
