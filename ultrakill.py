from pynput.keyboard import Key, KeyCode

from drawer import Drawer


class UltrakillDrawer(Drawer):
    game_url = "https://html-classic.itch.zone/html/15139480/ultrakill/index.html"
    loading_url = (
        "https://cdn.xn--d1ah4a.com/images/11b3680a-4429-490f-918a-45caca90882b.jpg"
    )
    mouse = True

    def _on_key_release(self, key: Key | KeyCode):
        super()._on_key_release(key)
        if key == Key.enter:
            self.lock_mouse = True

    async def sync_canvas(self):
        assert self.itd_canvas
        assert self.game_canvas

        await self.itd_canvas.evaluate(
            """async (element, src) => {
                img = new Image();
                img.src = src;
                await img.decode();
                context = element.getContext("2d");
                context.drawImage(img, 0, 0, element.width, element.height);
                //context.fillStyle = "#fff";
                //context.fillText("Загрузка..", 10, 50);
            }""",
            await self.game_canvas.evaluate(
                """
                (element, quality) => new Promise(resolve => {
                      requestAnimationFrame(() => {
                          resolve(element.toDataURL('image/jpeg', quality));
                      });
                  })
                """,
                self.quality
            )
        )
