"""

    Global Variable Class for tracking gamestate

"""
from dataclasses import dataclass

#Constants
WIDTH = 1280
HEIGHT = 720

#Global Variable Class
@dataclass
class GlobalState:
    running: bool = True
    w_width: int = WIDTH
    w_height: int = HEIGHT
    square_size: int = 100
    board_dim: int = 8
    board_origin: tuple = (0, 0)

