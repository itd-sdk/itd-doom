from asyncio import new_event_loop

import click
from playwright.async_api import async_playwright

from doom import DoomDrawer
from minecraft import MinecraftDrawer
from ultrakill import UltrakillDrawer

loop = new_event_loop()


@click.group()
def cli():
    pass


@cli.command()
@click.option("-q", "--quality", help="Out image quality", default=0.5, type=float)
def minecraft(quality: float = 0.5):
    async def main():
        async with async_playwright() as p:
            drawer: MinecraftDrawer = MinecraftDrawer.__new__(MinecraftDrawer)
            await drawer.__init__(p, loop, quality)
            await drawer.run()

    loop.run_until_complete(main())


@cli.command()
@click.option("-q", "--quality", help="Out image quality", default=0.5, type=float)
def doom(quality: float = 1):
    async def main():
        async with async_playwright() as p:
            drawer: DoomDrawer = DoomDrawer.__new__(DoomDrawer)
            await drawer.__init__(p, loop, quality)
            await drawer.run()

    loop.run_until_complete(main())


@cli.command()
@click.option("-q", "--quality", help="Out image quality", default=0.5, type=float)
def ultrakill(quality: float = 1):
    async def main():
        async with async_playwright() as p:
            drawer: UltrakillDrawer = UltrakillDrawer.__new__(UltrakillDrawer)
            await drawer.__init__(p, loop, quality)
            await drawer.run()

    loop.run_until_complete(main())


cli()
