from typing import Dict, List

from .models import LevelNode


LEVELS: List[LevelNode] = [
    LevelNode(1, 125, 255, "Greenwatch Road", "The first goblin raid", "Easy", "Verdant Lowlands"),
    LevelNode(2, 250, 355, "Old Mill", "Defend the river crossing", "Easy", "Verdant Lowlands"),
    LevelNode(3, 420, 305, "Sunfield Crossing", "Protect the trade route", "Easy", "Golden Fields"),
    LevelNode(4, 525, 425, "Pinefang Pass", "Fast enemies appear", "Normal", "Whispering Woods"),
    LevelNode(5, 665, 355, "Moonwell Grove", "Armored invaders arrive", "Normal", "Whispering Woods"),
    LevelNode(6, 800, 455, "Ashen Outpost", "Survive a long siege", "Hard", "Ashen Frontier"),
    LevelNode(7, 955, 365, "Dreadmarsh", "The road splits in two", "Hard", "Ashen Frontier"),
    LevelNode(8, 1085, 475, "Blackstone Gate", "Defend the mountain gate", "Hard", "Iron Mountains"),
    LevelNode(9, 1030, 565, "Stormpeak", "Winds empower the enemy", "Very Hard", "Iron Mountains"),
    LevelNode(10, 835, 595, "Ironvale Citadel", "The final assault", "Boss", "Ironvale"),
]

LEVEL_BY_ID: Dict[int, LevelNode] = {level.level_id: level for level in LEVELS}
