from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..root import IronvaleRoot


def handle_touch(ui: "IronvaleRoot", x: float, y: float) -> None:
    if ui.inside(x, y, 420, 385, 440, 62):
        ui.music_enabled = not ui.music_enabled
        ui.persist()
        ui.redraw()
    elif ui.inside(x, y, 420, 305, 440, 62):
        ui.sfx_enabled = not ui.sfx_enabled
        ui.persist()
        ui.redraw()
    elif ui.inside(x, y, 420, 220, 440, 62):
        ui.reset_progress()
    elif ui.inside(x, y, 470, 125, 340, 62):
        ui.close_overlay()
    elif not ui.inside(x, y, 365, 90, 550, 500):
        ui.close_overlay()


def draw(ui: "IronvaleRoot") -> None:
    ui.rect(0, 0, 1280, 720, (0, 0, 0, 0.55))
    ui.rect(365, 90, 550, 500, (0.045, 0.04, 0.03, 0.98), 26)
    ui.rect(377, 102, 526, 476, (0.16, 0.13, 0.075, 0.95), 20)

    ui.text("SETTINGS", 640, 530, 36, (1, 0.81, 0.31, 1))
    ui.button(
        420,
        385,
        440,
        62,
        f"MUSIC: {'ON' if ui.music_enabled else 'OFF'}",
        (0.28, 0.47, 0.30, 1) if ui.music_enabled else (0.35, 0.28, 0.24, 1),
        text_size=20,
    )
    ui.button(
        420,
        305,
        440,
        62,
        f"SOUND EFFECTS: {'ON' if ui.sfx_enabled else 'OFF'}",
        (0.28, 0.47, 0.30, 1) if ui.sfx_enabled else (0.35, 0.28, 0.24, 1),
        text_size=20,
    )
    ui.button(
        420,
        220,
        440,
        62,
        "RESET CAMPAIGN PROGRESS",
        (0.50, 0.24, 0.18, 1),
        text_size=18,
    )
    ui.button(470, 125, 340, 62, "CLOSE", (0.32, 0.36, 0.31, 1), text_size=20)
