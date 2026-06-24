from asyncio import new_event_loop, run_coroutine_threadsafe, sleep
from os import getenv
from time import time

# from keyboard import add_hotkey # keyboard requires root but playwright doesn't run with root so i switched to pynput
from playwright.async_api import async_playwright
from playwright_localstorage import AsyncLocalStorageAccessor
from pynput.keyboard import Key, Listener

loop = new_event_loop()


async def main():
    async with async_playwright() as p:
        print("\rinit browser", end="")
        itd = await p.firefox.launch(headless=False)
        doom = await p.firefox.launch()

        context = await itd.new_context()
        await context.add_cookies(
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
        itd_page = await context.new_page()
        await itd_page.goto("https://xn--d1ah4a.com/")

        accessor = AsyncLocalStorageAccessor(itd_page)
        await accessor.set("seen_announcements", '["new-feed-2026-06-15"]')
        await itd_page.reload()

        await itd_page.get_by_title("Нарисовать").click()
        itd_canvas = itd_page.locator("canvas")
        # (w, h) = canvas.evaluate("(element) => (element.width, element.height)")

        await itd_canvas.evaluate(
            "(element) => {element.parentNode.appendChild(element.cloneNode(true)); element.remove()}"  # remove all event listeners (to user cant draw)
        )
        await itd_canvas.evaluate(
            '(element) => {img = new Image(); img.src = "https://cdn.xn--d1ah4a.com/images/f3c3b9a0-6b4e-484b-878b-5b9e759051d3.jpg"; img.onload = () => {element.getContext("2d").drawImage(img, 0, 0, element.width, element.height)}}'
        )
        print("\rstart game      ", end="")

        await itd_page.wait_for_timeout(2000)

        doom_page = await doom.new_page()
        await doom_page.goto("https://diekmann.github.io/wasm-fizzbuzz/doom/")
        doom_canvas = doom_page.locator("canvas")

        async def update():
            await itd_canvas.evaluate(
                '(element, src) => {img = new Image(); img.src = src; element.getContext("2d").drawImage(img, 0, 0, element.width, element.height)}',
                await doom_canvas.evaluate("(element) => element.toDataURL()")
            )

        keys = (Key.enter, Key.down, Key.up, Key.left, Key.right, Key.space, Key.ctrl)

        def on_press(key: Key):
            if key not in keys:
                return
            run_coroutine_threadsafe(
                doom_page.locator(f"#{key.name}Button").evaluate(
                    '(element) => element.dispatchEvent(new Event("touchstart"))'
                ),
                loop
            )

        def on_release(key: Key):
            if key not in keys:
                return
            run_coroutine_threadsafe(
                doom_page.locator(f"#{key.name}Button").evaluate(
                    '(element) => element.dispatchEvent(new Event("touchend"))'
                ),
                loop
            )

        Listener(on_press=on_press, on_release=on_release).start()

        frames = []
        while True:
            await update()
            await sleep(0.001)
            frames.append(time())
            frames = [f for f in frames if f > time() - 10]
            print(
                f"\r{round(len(frames) / 10, 2)} fps // {await doom_page.locator('#animationfps_stats').text_content()} game fps    ",
                end=""
            )


run_coroutine_threadsafe(main(), loop)
loop.run_forever()
