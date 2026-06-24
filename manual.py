from pathlib import Path

from keyboard import wait
from PIL import Image
from pyautogui import Point, click
from pyautogui import mouseDown as mouse_down
from pyautogui import mouseUp as mouse_up
from pyautogui import position as get_mouse_position


def select() -> Point:
    wait("shift")
    return get_mouse_position()


pallete = select()

colors = {
    color: Point(pallete.x + 28 * i, pallete.y)
    for i, color in enumerate(
        [
            (0, 0, 0),
            (255, 255, 255),
            (255, 59, 48),
            (255, 149, 0),
            (255, 204, 0),
            (52, 199, 89),
            (0, 122, 255),
            (88, 86, 214),
            (175, 82, 222),
            (255, 45, 85),
            (142, 142, 147),
            (0, 199, 190)
        ]
    )
}


def _color_dist(c1: tuple, c2: tuple) -> int:
    return (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2


def snap_to_palette(color: tuple) -> tuple:
    # print([_color_dist(c, color) for c in colors.keys()])
    return colors[min(colors.keys(), key=lambda c: _color_dist(c, color))]


# class PixelAccess:
#     def __init__(self):
#         self.data: dict[tuple[int, int], int] = {}

#     def __getitem__(self, xy: tuple[int, int]) -> int:
#         return self.data[xy]

#     def __setitem__(self, xy: tuple[int, int], color: int) -> None:
#         self.data[xy] = color


def draw(path: Path):
    image = Image.open(path).resize(
        ((bottom_right.x - top_left.x) // 10, (bottom_right.y - top_left.y) // 10)
    )
    print(
        f"draw {path} size={(bottom_right.x - top_left.x) // 10}x{(bottom_right.y - top_left.y) // 10}"
    )
    pixels = image.load()
    assert pixels

    current_color = colors[(0, 0, 0)]
    click(current_color)
    is_down = False

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            pixel = pixels[x, y]
            assert isinstance(pixel, tuple)

            # for x in range(image.size[0] - 1):
            #     for y in range(image.size[1] - 1):
            #         pixel = bw[x, y]

            color = snap_to_palette(pixel)
            if color != current_color:
                current_color = color
                click(current_color)

            pos = ((x * 10) + top_left.x, (y * 10) + top_left.y)
            if not is_down:
                mouse_down(pos)
                is_down = True
            # else:
            #     print("move")
            #     move_to(pos)
            if y < image.size[1] - 1:
                next_pixel = pixels[x, y + 1]
                assert isinstance(next_pixel, tuple)
                if snap_to_palette(next_pixel) == current_color:
                    continue

            mouse_up(pos)
            is_down = False

            # if y < image.size[1]:
            #     next_pixel = bw[x, y + 1]
            #     assert isinstance(next_pixel, int)
            #     if pixel < 100 and next_pixel >= 100:
            #         move_to((x * 10) + top_left.x, (y * 10) + top_left.y)
            # else:
            #     move_to((x * 10) + top_left.x, (y * 10) + top_left.y)


top_left = select()
bottom_right = select()
draw(Path("loading.png"))
