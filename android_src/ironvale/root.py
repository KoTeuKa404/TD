from __future__ import annotations

import math
import os
from typing import Dict, Optional

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.widget import Widget

from .constants import Point
from .levels import LEVELS, LEVEL_BY_ID
from .models import LevelNode
from .rendering import CanvasRenderer
from .save_manager import SaveData, SaveManager
from .screens import menu, settings, world_map


class IronvaleRoot(Widget, CanvasRenderer):
    """Application state, navigation and input routing."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.screen = "menu"
        self.overlay: Optional[str] = None
        self.selected_level_id: Optional[int] = None

        self.unlocked_level = 1
        self.level_stars: Dict[str, int] = {}
        self.music_enabled = True
        self.sfx_enabled = True

        self.toast_text = ""
        self.toast_timer = 0.0
        self.animation_time = 0.0

        asset_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
            "menu",
        )
        self.initialize_renderer(asset_root)

        app = App.get_running_app()
        user_data_dir = app.user_data_dir if app else "."
        self.save_manager = SaveManager(
            os.path.join(user_data_dir, "ironvale_progress.json"),
            len(LEVELS),
        )
        self.load_progress()

        Clock.schedule_interval(self.update, 1.0 / 30.0)
        self.bind(pos=self._on_geometry_changed, size=self._on_geometry_changed)
        Window.bind(on_keyboard=self._on_keyboard)

    @staticmethod
    def point_distance(first: Point, second: Point) -> float:
        return math.hypot(first[0] - second[0], first[1] - second[1])

    @staticmethod
    def inside(
        x: float,
        y: float,
        left: float,
        bottom: float,
        width: float,
        height: float,
    ) -> bool:
        return left <= x <= left + width and bottom <= y <= bottom + height

    @property
    def selected_level(self) -> Optional[LevelNode]:
        if self.selected_level_id is None:
            return None
        return LEVEL_BY_ID.get(self.selected_level_id)

    def load_progress(self) -> None:
        data = self.save_manager.load()
        self.unlocked_level = data.unlocked_level
        self.level_stars = data.level_stars
        self.music_enabled = data.music_enabled
        self.sfx_enabled = data.sfx_enabled

    def persist(self) -> None:
        try:
            self.save_manager.save(
                SaveData(
                    unlocked_level=self.unlocked_level,
                    level_stars=self.level_stars,
                    music_enabled=self.music_enabled,
                    sfx_enabled=self.sfx_enabled,
                )
            )
        except OSError:
            self.show_toast("Could not save progress")

    def open_world_map(self) -> None:
        self.screen = "world_map"
        self.overlay = None
        if self.selected_level_id is None:
            self.selected_level_id = self.unlocked_level
        self.redraw()

    def open_menu(self) -> None:
        self.screen = "menu"
        self.overlay = None
        self.selected_level_id = None
        self.redraw()

    def open_settings(self) -> None:
        self.overlay = "settings"
        self.redraw()

    def close_overlay(self) -> None:
        self.overlay = None
        self.redraw()

    def open_level(self) -> None:
        level = self.selected_level
        if level is None:
            self.show_toast("Select a level first")
            return
        if not self.is_level_unlocked(level.level_id):
            self.show_toast("This level is locked")
            return
        self.show_toast(f"Level {level.level_id} is ready for gameplay integration")

    def is_level_unlocked(self, level_id: int) -> bool:
        return level_id <= self.unlocked_level

    def reset_progress(self) -> None:
        self.unlocked_level = 1
        self.level_stars = {}
        self.selected_level_id = 1
        self.persist()
        self.close_overlay()
        self.show_toast("Progress reset")

    def show_toast(self, text: str, duration: float = 2.4) -> None:
        self.toast_text = text
        self.toast_timer = duration
        self.redraw()

    def update(self, dt: float) -> None:
        dt = min(dt, 0.1)
        self.animation_time += dt
        if self.toast_timer > 0:
            self.toast_timer = max(0.0, self.toast_timer - dt)
        self.redraw()

    def _on_geometry_changed(self, *_args) -> None:
        self.clear_text_cache()
        self.redraw()

    def _touch_to_virtual(self, touch) -> Point:
        return (
            (touch.x - self.viewport_x) / self.scale,
            (touch.y - self.viewport_y) / self.scale,
        )

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        x, y = self._touch_to_virtual(touch)

        if self.overlay == "settings":
            settings.handle_touch(self, x, y)
        elif self.screen == "menu":
            menu.handle_touch(self, x, y)
        elif self.screen == "world_map":
            world_map.handle_touch(self, x, y)

        return True

    def _on_keyboard(self, _window, key, _scancode, _codepoint, _modifiers):
        if key not in (27, 1001):
            return False
        if self.overlay is not None:
            self.close_overlay()
            return True
        if self.screen == "world_map":
            self.open_menu()
            return True
        return False

    def redraw(self) -> None:
        self.canvas.clear()

        with self.canvas:
            self.color((0.018, 0.028, 0.025, 1))
            Rectangle(pos=self.pos, size=self.size)

            if self.screen == "menu":
                menu.draw(self)
            elif self.screen == "world_map":
                world_map.draw(self)

            if self.overlay == "settings":
                settings.draw(self)

            if self.toast_timer > 0:
                self.draw_toast()

    def draw_toast(self) -> None:
        alpha = max(0.0, min(1.0, self.toast_timer / 0.35))
        self.rect(370, 610, 540, 48, (0.025, 0.025, 0.02, 0.90 * alpha), 12)
        self.text(self.toast_text, 640, 634, 18, (1, 0.90, 0.61, alpha))
