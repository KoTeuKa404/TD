"""
Ironvale Defense — menu and world-map prototype for Kivy / Android.

Implemented:
- Main menu
- World map with connected level points
- Locked/unlocked level states
- Level selection panel
- Persistent JSON progress/settings
- Android back-button handling
- Asset-free adaptive rendering on a virtual 1280x720 canvas

The battle screen is intentionally not connected yet. The selected level can be
passed to the future gameplay screen through `open_level()`.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle, Triangle
from kivy.uix.widget import Widget


VW = 1280.0
VH = 720.0

RGBA = Tuple[float, float, float, float]
Point = Tuple[float, float]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def point_distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


@dataclass(frozen=True)
class LevelNode:
    level_id: int
    x: float
    y: float
    title: str
    subtitle: str
    difficulty: str
    region: str


LEVELS: List[LevelNode] = [
    LevelNode(1, 135, 185, "Greenwatch Road", "The first goblin raid", "Easy", "Verdant Lowlands"),
    LevelNode(2, 270, 275, "Old Mill", "Defend the river crossing", "Easy", "Verdant Lowlands"),
    LevelNode(3, 410, 205, "Broken Bridge", "Hold both approaches", "Normal", "Verdant Lowlands"),
    LevelNode(4, 550, 325, "Pinefang Pass", "Fast enemies appear", "Normal", "Whispering Woods"),
    LevelNode(5, 695, 240, "Moonwell Grove", "Armored invaders arrive", "Normal", "Whispering Woods"),
    LevelNode(6, 835, 355, "Ashen Outpost", "Survive a long siege", "Hard", "Ashen Frontier"),
    LevelNode(7, 975, 275, "Dreadmarsh", "The road splits in two", "Hard", "Ashen Frontier"),
    LevelNode(8, 1110, 405, "Blackstone Gate", "Defend the mountain gate", "Hard", "Iron Mountains"),
    LevelNode(9, 960, 535, "Stormpeak", "Winds empower the enemy", "Very Hard", "Iron Mountains"),
    LevelNode(10, 760, 565, "Ironvale Citadel", "The final assault", "Boss", "Ironvale"),
]

LEVEL_BY_ID: Dict[int, LevelNode] = {level.level_id: level for level in LEVELS}


class IronvaleRoot(Widget):
    """Single-widget UI state machine rendered with Kivy canvas primitives."""

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

        self._text_cache: Dict[Tuple, object] = {}
        self._texture_cache: Dict[str, object] = {}
        self._asset_root = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets", "menu"
        )
        self._animation_time = 0.0

        self.load_save()

        Clock.schedule_interval(self.update, 1.0 / 30.0)
        self.bind(pos=self._on_geometry_changed, size=self._on_geometry_changed)
        Window.bind(on_keyboard=self._on_keyboard)

    # ------------------------------------------------------------------
    # Scaling and persistence
    # ------------------------------------------------------------------

    @property
    def scale(self) -> float:
        if not self.width or not self.height:
            return 1.0
        return min(self.width / VW, self.height / VH)

    @property
    def sx(self) -> float:
        return self.scale

    @property
    def sy(self) -> float:
        return self.scale

    @property
    def viewport_x(self) -> float:
        return self.x + (self.width - VW * self.scale) / 2.0

    @property
    def viewport_y(self) -> float:
        return self.y + (self.height - VH * self.scale) / 2.0

    def vx(self, value: float) -> float:
        return self.viewport_x + value * self.scale

    def vy(self, value: float) -> float:
        return self.viewport_y + value * self.scale

    def _on_geometry_changed(self, *_args) -> None:
        self._text_cache.clear()
        self.redraw()

    def save_path(self) -> str:
        app = App.get_running_app()
        root = app.user_data_dir if app else "."
        return os.path.join(root, "ironvale_progress.json")

    def load_save(self) -> None:
        try:
            with open(self.save_path(), "r", encoding="utf-8") as file:
                data = json.load(file)

            self.unlocked_level = int(
                clamp(int(data.get("unlocked_level", 1)), 1, len(LEVELS))
            )

            raw_stars = data.get("level_stars", {})
            if isinstance(raw_stars, dict):
                self.level_stars = {
                    str(level_id): int(clamp(int(stars), 0, 3))
                    for level_id, stars in raw_stars.items()
                    if str(level_id).isdigit()
                }

            self.music_enabled = bool(data.get("music_enabled", True))
            self.sfx_enabled = bool(data.get("sfx_enabled", True))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.unlocked_level = 1
            self.level_stars = {}
            self.music_enabled = True
            self.sfx_enabled = True

    def save(self) -> None:
        payload = {
            "unlocked_level": self.unlocked_level,
            "level_stars": self.level_stars,
            "music_enabled": self.music_enabled,
            "sfx_enabled": self.sfx_enabled,
        }

        try:
            directory = os.path.dirname(self.save_path())
            if directory:
                os.makedirs(directory, exist_ok=True)

            temp_path = self.save_path() + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
                file.flush()
                os.fsync(file.fileno())

            os.replace(temp_path, self.save_path())
        except OSError:
            self.show_toast("Could not save progress")

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

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
        """Future integration point for the battle/gameplay screen."""
        level = self.selected_level
        if level is None:
            self.show_toast("Select a level first")
            return

        if not self.is_level_unlocked(level.level_id):
            self.show_toast("This level is locked")
            return

        # Replace this toast with:
        # self.screen = "game"
        # self.current_level_id = level.level_id
        # self.game_controller.load_level(level.level_id)
        self.show_toast(f"Level {level.level_id} is ready for gameplay integration")

    @property
    def selected_level(self) -> Optional[LevelNode]:
        if self.selected_level_id is None:
            return None
        return LEVEL_BY_ID.get(self.selected_level_id)

    def is_level_unlocked(self, level_id: int) -> bool:
        return level_id <= self.unlocked_level

    def reset_progress(self) -> None:
        self.unlocked_level = 1
        self.level_stars = {}
        self.selected_level_id = 1
        self.save()
        self.close_overlay()
        self.show_toast("Progress reset")

    def show_toast(self, text: str, duration: float = 2.4) -> None:
        self.toast_text = text
        self.toast_timer = duration
        self.redraw()

    def update(self, dt: float) -> None:
        dt = min(dt, 0.1)
        self._animation_time += dt

        if self.toast_timer > 0:
            self.toast_timer = max(0.0, self.toast_timer - dt)

        # Redraw is cheap here and keeps the selected level pulse animated.
        self.redraw()

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def _touch_to_virtual(self, touch) -> Point:
        return (
            (touch.x - self.viewport_x) / self.scale,
            (touch.y - self.viewport_y) / self.scale,
        )

    @staticmethod
    def _inside(x: float, y: float, left: float, bottom: float, width: float, height: float) -> bool:
        return left <= x <= left + width and bottom <= y <= bottom + height

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        x, y = self._touch_to_virtual(touch)

        if self.overlay == "settings":
            self._handle_settings_touch(x, y)
            return True

        if self.screen == "menu":
            self._handle_menu_touch(x, y)
            return True

        if self.screen == "world_map":
            self._handle_map_touch(x, y)
            return True

        return True

    def _handle_menu_touch(self, x: float, y: float) -> None:
        # START button.
        if self._inside(x, y, 425, 87, 430, 193):
            self.open_world_map()
            return

        # Circular settings button.
        if point_distance((x, y), (1216, 65)) <= 52:
            self.open_settings()

    def _handle_map_touch(self, x: float, y: float) -> None:
        if self._inside(x, y, 22, 652, 150, 50):
            self.open_menu()
            return

        if self._inside(x, y, 1088, 652, 170, 50):
            self.open_settings()
            return

        if self._inside(x, y, 1015, 24, 225, 82):
            self.open_level()
            return

        for level in LEVELS:
            if point_distance((x, y), (level.x, level.y)) <= 38:
                if self.is_level_unlocked(level.level_id):
                    self.selected_level_id = level.level_id
                    self.redraw()
                else:
                    self.show_toast(
                        f"Complete level {level.level_id - 1} to unlock this point"
                    )
                return

    def _handle_settings_touch(self, x: float, y: float) -> None:
        if self._inside(x, y, 420, 385, 440, 62):
            self.music_enabled = not self.music_enabled
            self.save()
            self.redraw()
        elif self._inside(x, y, 420, 305, 440, 62):
            self.sfx_enabled = not self.sfx_enabled
            self.save()
            self.redraw()
        elif self._inside(x, y, 420, 220, 440, 62):
            self.reset_progress()
        elif self._inside(x, y, 470, 125, 340, 62):
            self.close_overlay()
        elif not self._inside(x, y, 365, 90, 550, 500):
            self.close_overlay()

    def _on_keyboard(self, _window, key, _scancode, _codepoint, _modifiers):
        # Android back button and Escape.
        if key not in (27, 1001):
            return False

        if self.overlay is not None:
            self.close_overlay()
            return True

        if self.screen == "world_map":
            self.open_menu()
            return True

        return False

    # ------------------------------------------------------------------
    # Canvas helpers
    # ------------------------------------------------------------------

    @staticmethod
    def color(rgba: RGBA) -> None:
        Color(*rgba)

    def rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        rgba: RGBA,
        radius: float = 0,
    ) -> None:
        self.color(rgba)
        pos = (self.vx(x), self.vy(y))
        size = (width * self.sx, height * self.sy)

        if radius > 0:
            RoundedRectangle(
                pos=pos,
                size=size,
                radius=[(radius * self.scale,)],
            )
        else:
            Rectangle(pos=pos, size=size)

    def circle(self, x: float, y: float, radius: float, rgba: RGBA) -> None:
        self.color(rgba)
        Ellipse(
            pos=(self.vx(x - radius), self.vy(y - radius)),
            size=(radius * 2 * self.sx, radius * 2 * self.sy),
        )

    def line(
        self,
        points: List[Point],
        rgba: RGBA,
        width: float = 1.0,
        close: bool = False,
    ) -> None:
        scaled_points: List[float] = []
        for px, py in points:
            scaled_points.extend((self.vx(px), self.vy(py)))

        self.color(rgba)
        Line(
            points=scaled_points,
            width=width * self.scale,
            joint="round",
            cap="round",
            close=close,
        )

    def triangle(self, points: List[Point], rgba: RGBA) -> None:
        self.color(rgba)
        Triangle(points=[coord for point in points for coord in (self.vx(point[0]), self.vy(point[1]))])

    def text(
        self,
        value: str,
        x: float,
        y: float,
        size: float = 22,
        color: RGBA = (1, 1, 1, 1),
        anchor: str = "center",
    ) -> None:
        font_size = round(size * self.scale, 2)
        cache_key = (str(value), font_size, tuple(color))

        texture = self._text_cache.get(cache_key)
        if texture is None:
            label = CoreLabel(
                text=cache_key[0],
                font_size=font_size,
                color=color,
            )
            label.refresh()
            texture = label.texture
            self._text_cache[cache_key] = texture

        if anchor == "left":
            tx = self.vx(x)
        elif anchor == "right":
            tx = self.vx(x) - texture.width
        else:
            tx = self.vx(x) - texture.width / 2

        ty = self.vy(y) - texture.height / 2

        self.color((1, 1, 1, 1))
        Rectangle(texture=texture, pos=(tx, ty), size=texture.size)

    def asset_path(self, filename: str) -> str:
        return os.path.join(self._asset_root, filename)

    def texture(self, filename: str):
        texture = self._texture_cache.get(filename)
        if texture is None:
            texture = CoreImage(self.asset_path(filename)).texture
            self._texture_cache[filename] = texture
        return texture

    def image_asset(
        self,
        filename: str,
        x: float,
        y: float,
        width: float,
        height: float,
        opacity: float = 1.0,
    ) -> None:
        self.color((1, 1, 1, opacity))
        Rectangle(
            texture=self.texture(filename),
            pos=(self.vx(x), self.vy(y)),
            size=(width * self.scale, height * self.scale),
        )

    def fullscreen_image(self, filename: str) -> None:
        self.color((1, 1, 1, 1))
        Rectangle(
            texture=self.texture(filename),
            pos=self.pos,
            size=self.size,
        )

    def button(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        label: str,
        accent: RGBA,
        enabled: bool = True,
        text_size: float = 23,
    ) -> None:
        frame = (0.045, 0.04, 0.03, 0.96)
        fill = accent if enabled else (0.24, 0.25, 0.24, 1)
        text_color = (1, 0.94, 0.74, 1) if enabled else (0.58, 0.60, 0.58, 1)

        self.rect(x, y, width, height, frame, 13)
        self.rect(x + 4, y + 4, width - 8, height - 8, fill, 10)
        self.rect(x + 10, y + height - 13, width - 20, 4, (1, 1, 1, 0.10), 2)
        self.text(label, x + width / 2, y + height / 2 + 1, text_size, text_color)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def redraw(self) -> None:
        self.canvas.clear()

        with self.canvas:
            # Bars outside the 16:9 safe viewport on unusual aspect ratios.
            self.color((0.018, 0.028, 0.025, 1))
            Rectangle(pos=self.pos, size=self.size)

            if self.screen == "menu":
                self.draw_menu()
            elif self.screen == "world_map":
                self.draw_world_map()

            if self.overlay == "settings":
                self.draw_settings_overlay()

            if self.toast_timer > 0:
                self.draw_toast()

    def draw_menu(self) -> None:
        # The background is allowed to cover the whole physical display.
        # Interactive UI stays inside the centered 1280x720 safe area.
        self.fullscreen_image("background.png")

        # Positions match the supplied 16:9 composition.
        self.image_asset("logo.png", 345, 288, 590, 427)
        self.image_asset("start.png", 425, 87, 430, 193)
        self.image_asset("settings.png", 1170, 18, 92, 94)

    def draw_world_map(self) -> None:
        # Base terrain
        self.rect(0, 0, VW, VH, (0.14, 0.29, 0.19, 1))

        # Water
        self.circle(105, 545, 210, (0.08, 0.29, 0.36, 1))
        self.circle(50, 390, 150, (0.08, 0.29, 0.36, 1))
        self.circle(1210, 110, 170, (0.07, 0.26, 0.33, 1))

        # Terrain regions
        self.circle(320, 365, 290, (0.18, 0.38, 0.20, 1))
        self.circle(670, 390, 275, (0.13, 0.31, 0.18, 1))
        self.circle(1020, 390, 265, (0.26, 0.25, 0.18, 1))
        self.circle(870, 610, 190, (0.29, 0.31, 0.31, 1))

        # Forest clusters
        for fx, fy, radius in [
            (235, 410, 85),
            (485, 470, 70),
            (650, 410, 88),
            (815, 455, 64),
        ]:
            self.circle(fx, fy, radius, (0.08, 0.23, 0.12, 0.88))
            self.circle(fx - 25, fy + 20, radius * 0.66, (0.10, 0.29, 0.14, 0.9))

        # Mountains
        for mx, my, size in [
            (990, 570, 90),
            (1090, 545, 72),
            (1160, 515, 62),
            (870, 620, 72),
        ]:
            self.triangle(
                [(mx - size, my - size * 0.55), (mx, my + size), (mx + size, my - size * 0.55)],
                (0.31, 0.32, 0.31, 1),
            )
            self.triangle(
                [(mx - size * 0.28, my + size * 0.42), (mx, my + size), (mx + size * 0.28, my + size * 0.42)],
                (0.73, 0.76, 0.74, 0.72),
            )

        # Route shadow and road.
        route = [(level.x, level.y) for level in LEVELS]
        self.line(route, (0.09, 0.065, 0.035, 0.68), 22)
        self.line(route, (0.68, 0.48, 0.23, 1), 14)
        self.line(route, (0.92, 0.73, 0.39, 0.60), 2)

        # Top navigation bar.
        self.rect(0, 638, VW, 82, (0.035, 0.045, 0.035, 0.94))
        self.button(22, 652, 150, 50, "BACK", (0.37, 0.29, 0.18, 1), text_size=18)
        self.text("WORLD MAP", 640, 681, 31, (1, 0.83, 0.36, 1))
        self.button(1088, 652, 170, 50, "SETTINGS", (0.24, 0.38, 0.45, 1), text_size=17)

        # Level points.
        for level in LEVELS:
            self.draw_level_node(level)

        # Selected-level panel.
        self.draw_level_panel()

    def draw_level_node(self, level: LevelNode) -> None:
        unlocked = self.is_level_unlocked(level.level_id)
        selected = self.selected_level_id == level.level_id

        if selected:
            pulse = 44 + math.sin(self._animation_time * 4.0) * 4
            self.circle(level.x, level.y, pulse, (1, 0.78, 0.24, 0.15))
            self.circle(level.x, level.y, 38, (1, 0.88, 0.38, 0.20))

        # Shadow
        self.circle(level.x + 3, level.y - 5, 31, (0.03, 0.025, 0.02, 0.45))

        if unlocked:
            outer = (0.82, 0.57, 0.17, 1)
            inner = (0.27, 0.48, 0.18, 1)
            text_color = (1, 0.95, 0.72, 1)
        else:
            outer = (0.30, 0.31, 0.30, 1)
            inner = (0.16, 0.17, 0.16, 1)
            text_color = (0.56, 0.58, 0.56, 1)

        self.circle(level.x, level.y, 31, (0.06, 0.05, 0.035, 1))
        self.circle(level.x, level.y, 27, outer)
        self.circle(level.x, level.y, 21, inner)
        self.text(str(level.level_id), level.x, level.y + 1, 20, text_color)

        if not unlocked:
            # Small lock.
            self.rect(level.x - 8, level.y - 10, 16, 13, (0.08, 0.08, 0.075, 1), 3)
            self.line(
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

        stars = self.level_stars.get(str(level.level_id), 0)
        for index in range(3):
            star_x = level.x - 14 + index * 14
            star_color = (
                (1, 0.78, 0.18, 1)
                if index < stars
                else (0.11, 0.10, 0.08, 0.75)
            )
            self.circle(star_x, level.y - 39, 4.3, star_color)

    def draw_level_panel(self) -> None:
        self.rect(0, 0, VW, 126, (0.035, 0.04, 0.03, 0.96))

        level = self.selected_level
        if level is None:
            self.text(
                "Select an unlocked point on the map",
                640,
                62,
                24,
                (0.76, 0.80, 0.68, 1),
            )
            return

        unlocked = self.is_level_unlocked(level.level_id)

        self.text(
            f"LEVEL {level.level_id}",
            32,
            88,
            18,
            (1, 0.72, 0.24, 1) if unlocked else (0.58, 0.59, 0.57, 1),
            anchor="left",
        )
        self.text(level.title, 32, 55, 27, (0.94, 0.91, 0.72, 1), anchor="left")
        self.text(level.subtitle, 32, 25, 17, (0.65, 0.72, 0.63, 1), anchor="left")

        self.text("REGION", 575, 83, 14, (0.55, 0.60, 0.53, 1), anchor="left")
        self.text(level.region, 575, 55, 19, (0.86, 0.84, 0.68, 1), anchor="left")

        self.text("DIFFICULTY", 790, 83, 14, (0.55, 0.60, 0.53, 1), anchor="left")
        difficulty_color = {
            "Easy": (0.48, 0.82, 0.35, 1),
            "Normal": (0.93, 0.76, 0.28, 1),
            "Hard": (0.94, 0.46, 0.23, 1),
            "Very Hard": (0.88, 0.27, 0.22, 1),
            "Boss": (0.75, 0.35, 0.88, 1),
        }.get(level.difficulty, (0.8, 0.8, 0.8, 1))
        self.text(level.difficulty, 790, 53, 20, difficulty_color, anchor="left")

        self.button(
            1015,
            24,
            225,
            82,
            "START LEVEL" if unlocked else "LOCKED",
            (0.31, 0.57, 0.20, 1),
            enabled=unlocked,
            text_size=22,
        )

    def draw_settings_overlay(self) -> None:
        self.rect(0, 0, VW, VH, (0, 0, 0, 0.55))

        self.rect(365, 90, 550, 500, (0.045, 0.04, 0.03, 0.98), 26)
        self.rect(377, 102, 526, 476, (0.16, 0.13, 0.075, 0.95), 20)

        self.text("SETTINGS", 640, 530, 36, (1, 0.81, 0.31, 1))

        self.button(
            420,
            385,
            440,
            62,
            f"MUSIC: {'ON' if self.music_enabled else 'OFF'}",
            (0.28, 0.47, 0.30, 1) if self.music_enabled else (0.35, 0.28, 0.24, 1),
            text_size=20,
        )
        self.button(
            420,
            305,
            440,
            62,
            f"SOUND EFFECTS: {'ON' if self.sfx_enabled else 'OFF'}",
            (0.28, 0.47, 0.30, 1) if self.sfx_enabled else (0.35, 0.28, 0.24, 1),
            text_size=20,
        )
        self.button(
            420,
            220,
            440,
            62,
            "RESET CAMPAIGN PROGRESS",
            (0.50, 0.24, 0.18, 1),
            text_size=18,
        )
        self.button(
            470,
            125,
            340,
            62,
            "CLOSE",
            (0.32, 0.36, 0.31, 1),
            text_size=20,
        )

    def draw_toast(self) -> None:
        alpha = clamp(self.toast_timer / 0.35, 0.0, 1.0)
        self.rect(370, 610, 540, 48, (0.025, 0.025, 0.02, 0.90 * alpha), 12)
        self.text(
            self.toast_text,
            640,
            634,
            18,
            (1, 0.90, 0.61, alpha),
        )


class IronvaleApp(App):
    title = "Ironvale Defense"

    def build(self):
        Window.clearcolor = (0.02, 0.035, 0.03, 1)
        return IronvaleRoot()


if __name__ == "__main__":
    IronvaleApp().run()