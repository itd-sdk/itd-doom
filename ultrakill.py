from pynput.keyboard import Key, KeyCode

from drawer import Drawer


class UltrakillDrawer(Drawer):
    game_url = "https://html-classic.itch.zone/html/15139480/ultrakill/index.html"
    loading_url = (
        "https://cdn.xn--d1ah4a.com/images/15d69e8f-1f34-453e-9b62-6292c2d9e768.jpg"
    )
    mouse = True
    _get_image_script = """
    (element, quality) => new Promise(resolve => {
          requestAnimationFrame(() => {
              resolve(element.toDataURL('image/jpeg', quality));
          });
      })
    """

    def _on_key_release(self, key: Key | KeyCode):
        super()._on_key_release(key)
        if key == Key.ctrl:
            self.lock_mouse = True
