from drawer import Drawer


class MinecraftDrawer(Drawer):
    game_url = "https://mcraft.fun/"
    loading_url = (
        "https://cdn.xn--d1ah4a.com/images/2efc31b0-87b3-4844-b9e5-54be74168623.jpg"
    )
    mouse = True
    lock_mouse = True

    async def open_game(self):
        await super().open_game()
        assert self.game_page
        await self.game_page.get_by_text("Singleplayer").click()
        await self.game_page.get_by_text("Create New World").click()
        await self.game_page.get_by_placeholder("World name").type(
            "itd-drawer world (by itd-sdk) 676767766767"
        )
        await self.game_page.get_by_text("Create", exact=True).click()
