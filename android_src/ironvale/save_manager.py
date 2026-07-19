from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class SaveData:
    unlocked_level: int = 1
    level_stars: Dict[str, int] = field(default_factory=dict)
    music_enabled: bool = True
    sfx_enabled: bool = True


def clamp_int(value: object, low: int, high: int, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(low, min(high, parsed))


class SaveManager:
    def __init__(self, path: str, level_count: int) -> None:
        self.path = path
        self.level_count = level_count

    def load(self) -> SaveData:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                payload = json.load(file)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return SaveData()

        raw_stars = payload.get("level_stars", {})
        stars: Dict[str, int] = {}
        if isinstance(raw_stars, dict):
            for level_id, amount in raw_stars.items():
                key = str(level_id)
                if key.isdigit():
                    stars[key] = clamp_int(amount, 0, 3, 0)

        return SaveData(
            unlocked_level=clamp_int(
                payload.get("unlocked_level", 1), 1, self.level_count, 1
            ),
            level_stars=stars,
            music_enabled=bool(payload.get("music_enabled", True)),
            sfx_enabled=bool(payload.get("sfx_enabled", True)),
        )

    def save(self, data: SaveData) -> None:
        payload = {
            "unlocked_level": data.unlocked_level,
            "level_stars": data.level_stars,
            "music_enabled": data.music_enabled,
            "sfx_enabled": data.sfx_enabled,
        }

        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        temporary_path = self.path + ".tmp"
        with open(temporary_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, self.path)
