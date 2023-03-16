"""

    Global Variable Class for tracking colors of objects and text

"""
from dataclasses import dataclass

# Define Colors 
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 125, 0)
YELLOW = (255, 225, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)
MAGENTA = (255, 0, 125)

#Global Variable Class
@dataclass
class GlobalColors:
    background: tuple = BLACK
    black_square: tuple = GRAY
    white_square: tuple = WHITE