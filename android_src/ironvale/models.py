from dataclasses import dataclass


@dataclass(frozen=True)
class LevelNode:
    level_id: int
    x: float
    y: float
    title: str
    subtitle: str
    difficulty: str
    region: str
