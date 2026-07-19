from __future__ import annotations

import os
from typing import Dict, List, Tuple

from kivy.core.image import Image as CoreImage
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle, Triangle

from .constants import RGBA, Point, VH, VW


class CanvasRenderer:
    """Reusable scaled drawing helpers for the 1280x720 virtual canvas."""

    def initialize_renderer(self, asset_root: str) -> None:
        self._asset_root = asset_root
        self._text_cache: Dict[Tuple, object] = {}
        self._texture_cache: Dict[str, object] = {}

    @property
    def scale(self) -> float:
        if not self.width or not self.height:
            return 1.0
        return min(self.width / VW, self.height / VH)

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

    @staticmethod
    def color(rgba: RGBA) -> None:
        Color(*rgba)

    def clear_text_cache(self) -> None:
        self._text_cache.clear()

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
        size = (width * self.scale, height * self.scale)

        if radius > 0:
            RoundedRectangle(pos=pos, size=size, radius=[(radius * self.scale,)])
        else:
            Rectangle(pos=pos, size=size)

    def circle(self, x: float, y: float, radius: float, rgba: RGBA) -> None:
        self.color(rgba)
        Ellipse(
            pos=(self.vx(x - radius), self.vy(y - radius)),
            size=(radius * 2 * self.scale, radius * 2 * self.scale),
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
        Triangle(
            points=[
                coordinate
                for point in points
                for coordinate in (self.vx(point[0]), self.vy(point[1]))
            ]
        )

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
            label = CoreLabel(text=cache_key[0], font_size=font_size, color=color)
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
        Rectangle(texture=self.texture(filename), pos=self.pos, size=self.size)

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
