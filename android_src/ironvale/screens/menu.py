from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..root import IronvaleRoot


def draw(ui: "IronvaleRoot") -> None:
    ui.fullscreen_image("background.png")
    ui.image_asset("logo.png", 345, 288, 590, 427)
    ui.image_asset("start.png", 425, 87, 430, 193)
    ui.image_asset("settings.png", 1170, 18, 92, 94)


def handle_touch(ui: "IronvaleRoot", x: float, y: float) -> None:
    if ui.inside(x, y, 425, 87, 430, 193):
        ui.open_world_map()
        return

    if ui.point_distance((x, y), (1216, 65)) <= 52:
        ui.open_settings()
