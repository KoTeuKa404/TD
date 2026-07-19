from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ..constants import BOTTOM_PANEL_H, TOP_BAR_H, TOP_BAR_Y, VH, VW
from ..levels import LEVELS
from ..models import LevelNode

if TYPE_CHECKING:
    from ..root import IronvaleRoot


def handle_touch(ui: "IronvaleRoot", x: float, y: float) -> None:
    if ui.inside(x, y, 22, 652, 150, 50):
        ui.open_menu()
        return

    if ui.inside(x, y, 1088, 652, 170, 50):
        ui.open_settings()
        return

    if ui.inside(x, y, 1015, 24, 225, 82):
        ui.open_level()
        return

    for level in LEVELS:
        if ui.point_distance((x, y), (level.x, level.y)) <= 38:
            if ui.is_level_unlocked(level.level_id):
                ui.selected_level_id = level.level_id
                ui.redraw()
            else:
                ui.show_toast(
                    f"Complete level {level.level_id - 1} to unlock this point"
                )
            return


def draw(ui: "IronvaleRoot") -> None:
    draw_backdrop(ui)
    draw_regions(ui)
    draw_route(ui)
    draw_landmarks(ui)
    draw_region_labels(ui)
    draw_world_ui(ui)


def draw_backdrop(ui: "IronvaleRoot") -> None:
    ui.rect(0, 0, VW, VH, (0.12, 0.19, 0.22, 1))
    ui.rect(0, 0, VW, BOTTOM_PANEL_H, (0.02, 0.03, 0.03, 1))
    ui.rect(0, TOP_BAR_Y, VW, VH - TOP_BAR_Y, (0.02, 0.03, 0.03, 1))

    ui.circle(88, 466, 238, (0.11, 0.44, 0.52, 1))
    ui.circle(25, 325, 136, (0.10, 0.38, 0.48, 1))
    ui.circle(1225, 505, 160, (0.12, 0.43, 0.50, 1))
    ui.circle(150, 460, 195, (0.70, 0.72, 0.46, 0.22))
    ui.circle(1180, 495, 132, (0.74, 0.74, 0.47, 0.17))


def draw_regions(ui: "IronvaleRoot") -> None:
    ui.circle(305, 375, 250, (0.28, 0.52, 0.24, 1))
    ui.circle(500, 468, 180, (0.17, 0.34, 0.16, 1))
    ui.circle(760, 430, 220, (0.38, 0.30, 0.18, 1))
    ui.circle(1030, 500, 250, (0.42, 0.42, 0.43, 1))
    ui.circle(885, 600, 130, (0.18, 0.39, 0.26, 1))
    ui.circle(615, 295, 150, (0.69, 0.61, 0.27, 1))

    ui.circle(255, 340, 175, (0.20, 0.44, 0.19, 0.95))
    ui.circle(545, 440, 140, (0.11, 0.24, 0.11, 0.95))
    ui.circle(760, 400, 175, (0.31, 0.22, 0.13, 0.95))
    ui.circle(1050, 470, 205, (0.35, 0.35, 0.37, 0.95))

    river = [
        (250, 160),
        (300, 220),
        (360, 280),
        (430, 325),
        (510, 350),
        (610, 365),
        (720, 390),
        (820, 430),
        (900, 485),
    ]
    ui.line(river, (0.08, 0.52, 0.67, 0.80), 24)
    ui.line(river, (0.62, 0.90, 1.0, 0.35), 9)


def draw_route(ui: "IronvaleRoot") -> None:
    route = [(level.x, level.y) for level in LEVELS]
    ui.line(route, (0.10, 0.07, 0.04, 0.72), 22)
    ui.line(route, (0.64, 0.47, 0.23, 1), 14)
    ui.line(route, (0.95, 0.80, 0.45, 0.45), 2)

    for level in LEVELS:
        draw_level_node(ui, level)


def draw_landmarks(ui: "IronvaleRoot") -> None:
    for fx, fy, radius in [
        (215, 395, 72),
        (330, 460, 64),
        (450, 408, 82),
        (570, 470, 62),
    ]:
        ui.circle(fx, fy, radius, (0.07, 0.20, 0.10, 0.90))
        ui.circle(fx - 22, fy + 16, radius * 0.62, (0.09, 0.28, 0.13, 0.95))

    ui.rect(520, 250, 120, 55, (0.84, 0.74, 0.32, 0.45), 14)
    ui.rect(610, 280, 95, 48, (0.78, 0.68, 0.28, 0.42), 12)
    ui.rect(558, 320, 130, 62, (0.89, 0.78, 0.37, 0.35), 16)

    ui.circle(820, 420, 48, (0.10, 0.20, 0.10, 0.55))
    ui.circle(900, 410, 30, (0.16, 0.26, 0.13, 0.48))
    ui.circle(870, 500, 38, (0.12, 0.22, 0.11, 0.52))

    for mx, my, size in [
        (970, 540, 74),
        (1050, 575, 98),
        (1150, 548, 72),
        (935, 610, 60),
        (1118, 625, 56),
    ]:
        ui.triangle(
            [
                (mx - size, my - size * 0.56),
                (mx, my + size),
                (mx + size, my - size * 0.56),
            ],
            (0.29, 0.30, 0.31, 1),
        )
        ui.triangle(
            [
                (mx - size * 0.28, my + size * 0.42),
                (mx, my + size),
                (mx + size * 0.28, my + size * 0.42),
            ],
            (0.76, 0.79, 0.79, 0.74),
        )

    draw_castle(ui, 115, 210, 0.8)
    draw_tower(ui, 600, 285, 0.78)
    draw_tower(ui, 810, 465, 0.70)
    draw_castle(ui, 858, 610, 0.90)
    draw_ship(ui, 68, 530, 0.9)
    draw_ship(ui, 160, 592, 0.7)


def draw_ship(ui: "IronvaleRoot", x: float, y: float, scale: float = 1.0) -> None:
    width = 34 * scale
    height = 10 * scale
    ui.line(
        [(x - width, y), (x - 3, y - height), (x + width, y)],
        (0.20, 0.13, 0.06, 1),
        7,
    )
    ui.line([(x, y), (x, y + 28 * scale)], (0.15, 0.10, 0.06, 1), 2)
    ui.triangle(
        [
            (x, y + 26 * scale),
            (x, y + 6 * scale),
            (x + 18 * scale, y + 16 * scale),
        ],
        (0.92, 0.91, 0.79, 0.95),
    )


def draw_tower(ui: "IronvaleRoot", x: float, y: float, scale: float = 1.0) -> None:
    ui.rect(
        x - 18 * scale,
        y - 22 * scale,
        36 * scale,
        50 * scale,
        (0.43, 0.34, 0.21, 1),
        5,
    )
    ui.rect(
        x - 22 * scale,
        y + 20 * scale,
        44 * scale,
        11 * scale,
        (0.18, 0.24, 0.47, 1),
        2,
    )
    ui.triangle(
        [
            (x - 27 * scale, y + 30 * scale),
            (x, y + 56 * scale),
            (x + 27 * scale, y + 30 * scale),
        ],
        (0.11, 0.19, 0.39, 1),
    )
    ui.rect(
        x - 7 * scale,
        y - 14 * scale,
        14 * scale,
        23 * scale,
        (0.18, 0.17, 0.13, 1),
        2,
    )
    ui.rect(
        x - 8 * scale,
        y + 1 * scale,
        16 * scale,
        11 * scale,
        (0.74, 0.83, 0.95, 0.65),
        2,
    )


def draw_castle(ui: "IronvaleRoot", x: float, y: float, scale: float = 1.0) -> None:
    wall = (0.74, 0.72, 0.66, 1)
    shadow = (0.46, 0.43, 0.37, 1)
    banner = (0.10, 0.30, 0.72, 1)

    ui.rect(x - 38 * scale, y - 12 * scale, 76 * scale, 44 * scale, wall, 6)
    ui.rect(x - 14 * scale, y + 18 * scale, 28 * scale, 38 * scale, wall, 4)
    ui.rect(x - 52 * scale, y + 2 * scale, 18 * scale, 44 * scale, wall, 4)
    ui.rect(x + 34 * scale, y + 2 * scale, 18 * scale, 44 * scale, wall, 4)

    for px in (-54, -40, -10, 0, 10, 40, 54):
        ui.rect(x + px * scale, y + 28 * scale, 8 * scale, 8 * scale, shadow, 2)
    for px in (-52, -34, -16, 2, 20, 38):
        ui.rect(x + px * scale, y + 40 * scale, 8 * scale, 8 * scale, shadow, 2)

    ui.rect(
        x - 8 * scale,
        y - 12 * scale,
        16 * scale,
        28 * scale,
        (0.39, 0.25, 0.11, 1),
        3,
    )
    ui.rect(x - 5 * scale, y, 10 * scale, 22 * scale, banner, 2)


def draw_region_labels(ui: "IronvaleRoot") -> None:
    labels = [
        (250, 520, "VERDANT LOWLANDS", (0.92, 1.00, 0.84, 0.85)),
        (515, 560, "WHISPERING WOODS", (0.84, 0.96, 0.84, 0.82)),
        (615, 205, "GOLDEN FIELDS", (0.99, 0.95, 0.72, 0.78)),
        (810, 575, "ASHEN FRONTIER", (1.00, 0.90, 0.82, 0.72)),
        (1040, 300, "IRON MOUNTAINS", (0.94, 0.97, 1.00, 0.78)),
    ]
    for x, y, label, color in labels:
        ui.text(label, x, y, 18, color)


def draw_world_ui(ui: "IronvaleRoot") -> None:
    ui.rect(0, TOP_BAR_Y, VW, TOP_BAR_H, (0.035, 0.045, 0.035, 0.94))
    ui.button(22, 652, 150, 50, "BACK", (0.37, 0.29, 0.18, 1), text_size=18)
    ui.text("WORLD MAP", 640, 681, 31, (1, 0.83, 0.36, 1))
    ui.button(
        1088,
        652,
        170,
        50,
        "SETTINGS",
        (0.24, 0.38, 0.45, 1),
        text_size=17,
    )
    draw_level_panel(ui)


def draw_level_node(ui: "IronvaleRoot", level: LevelNode) -> None:
    unlocked = ui.is_level_unlocked(level.level_id)
    selected = ui.selected_level_id == level.level_id

    if selected:
        pulse = 44 + math.sin(ui.animation_time * 4.0) * 4
        ui.circle(level.x, level.y, pulse, (1, 0.78, 0.24, 0.15))
        ui.circle(level.x, level.y, 38, (1, 0.88, 0.38, 0.22))

    ui.circle(level.x + 3, level.y - 5, 31, (0.03, 0.025, 0.02, 0.45))

    if unlocked:
        outer = (0.82, 0.57, 0.17, 1)
        inner = (0.27, 0.48, 0.18, 1)
        text_color = (1, 0.95, 0.72, 1)
    else:
        outer = (0.30, 0.31, 0.30, 1)
        inner = (0.16, 0.17, 0.16, 1)
        text_color = (0.56, 0.58, 0.56, 1)

    ui.circle(level.x, level.y, 31, (0.06, 0.05, 0.035, 1))
    ui.circle(level.x, level.y, 27, outer)
    ui.circle(level.x, level.y, 21, inner)
    ui.text(str(level.level_id), level.x, level.y + 1, 20, text_color)

    if not unlocked:
        ui.rect(level.x - 8, level.y - 10, 16, 13, (0.08, 0.08, 0.075, 1), 3)
        ui.line(
            [
                (level.x - 6, level.y + 2),
                (level.x - 6, level.y + 9),
                (level.x, level.y + 14),
                (level.x + 6, level.y + 9),
                (level.x + 6, level.y + 2),
            ],
            (0.48, 0.49, 0.47, 1),
            2,
        )

    stars = ui.level_stars.get(str(level.level_id), 0)
    for index in range(3):
        star_x = level.x - 14 + index * 14
        star_color = (
            (1, 0.78, 0.18, 1)
            if index < stars
            else (0.11, 0.10, 0.08, 0.75)
        )
        ui.circle(star_x, level.y - 39, 4.3, star_color)


def draw_level_panel(ui: "IronvaleRoot") -> None:
    ui.rect(0, 0, VW, BOTTOM_PANEL_H, (0.035, 0.04, 0.03, 0.96))

    level = ui.selected_level
    if level is None:
        ui.text(
            "Select an unlocked point on the map",
            640,
            62,
            24,
            (0.76, 0.80, 0.68, 1),
        )
        return

    unlocked = ui.is_level_unlocked(level.level_id)
    ui.text(
        f"LEVEL {level.level_id}",
        32,
        88,
        18,
        (1, 0.72, 0.24, 1) if unlocked else (0.58, 0.59, 0.57, 1),
        anchor="left",
    )
    ui.text(level.title, 32, 55, 27, (0.94, 0.91, 0.72, 1), anchor="left")
    ui.text(
        level.subtitle,
        32,
        25,
        17,
        (0.65, 0.72, 0.63, 1),
        anchor="left",
    )

    ui.text("REGION", 575, 83, 14, (0.55, 0.60, 0.53, 1), anchor="left")
    ui.text(level.region, 575, 55, 19, (0.86, 0.84, 0.68, 1), anchor="left")

    ui.text(
        "DIFFICULTY",
        790,
        83,
        14,
        (0.55, 0.60, 0.53, 1),
        anchor="left",
    )
    difficulty_color = {
        "Easy": (0.48, 0.82, 0.35, 1),
        "Normal": (0.93, 0.76, 0.28, 1),
        "Hard": (0.94, 0.46, 0.23, 1),
        "Very Hard": (0.88, 0.27, 0.22, 1),
        "Boss": (0.75, 0.35, 0.88, 1),
    }.get(level.difficulty, (0.8, 0.8, 0.8, 1))
    ui.text(level.difficulty, 790, 53, 20, difficulty_color, anchor="left")

    ui.button(
        1015,
        24,
        225,
        82,
        "START LEVEL" if unlocked else "LOCKED",
        (0.31, 0.57, 0.20, 1),
        enabled=unlocked,
        text_size=22,
    )
