"""
展品数据模型
定义展品的数据结构和相关枚举
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EmotionState(Enum):
    """情感状态枚举"""
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CONFUSED = "confused"


@dataclass
class Exhibit:
    """展品数据模型"""
    id: int
    x: float
    y: float
    theta: float
    description: str
    detailed_description: str
    popularity: float = 0.0
    visited: bool = False
    
    def __post_init__(self):
        """验证展品数据"""
        if self.id <= 0:
            raise ValueError("Exhibit ID must be positive")
        if self.popularity < 0.0 or self.popularity > 1.0:
            raise ValueError("Popularity must be between 0.0 and 1.0")

