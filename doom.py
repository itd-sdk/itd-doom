from asyncio import run_coroutine_threadsafe

from pynput.keyboard import Key, KeyCode

from drawer import Drawer


class DoomDrawer(Drawer):
    game_url = "https://diekmann.github.io/wasm-fizzbuzz/doom/"
    loading_url = (
        "https://cdn.xn--d1ah4a.com/images/f3c3b9a0-6b4e-484b-878b-5b9e759051d3.jpg"
    )
    keys = (Key.enter, Key.down, Key.up, Key.left, Key.right, Key.space, Key.ctrl)

    def _on_key_press(self, key: Key | KeyCode):
        super()._on_key_press(key)
        assert self.game_page
        if not isinstance(key, Key):
            return

        run_coroutine_threadsafe(
            self.game_page.locator(f"#{key.name}Button").evaluate(
                '(element) => element.dispatchEvent(new Event("touchstart"))'
            ),
            self.loop
        )

    def _on_key_release(self, key: Key | KeyCode):
        super()._on_key_release(key)
        assert self.game_page
        if not isinstance(key, Key):
            return

        run_coroutine_threadsafe(
            self.game_page.locator(f"#{key.name}Button").evaluate(
                '(element) => element.dispatchEvent(new Event("touchend"))'
            ),
            self.loop
        )

    async def _print_fps(self, frames: list[float | int]):
        assert self.game_page
        print(
            f"\r{round(len(frames) / 10, 2)} fps | {await self.game_page.locator('#animationfps_stats').text_content()} game fps     ",
            end=""
        )
