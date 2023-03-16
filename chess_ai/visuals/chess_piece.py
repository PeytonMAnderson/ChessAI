import pygame
import os

def load_images(dir: str):
    py_images = {}
    if os.path.exists(dir):
        for file in os.listdir(dir):
            d = dir + "/" + file
            piece = file.split('.')[0]
            py_images[piece] = pygame.image.load(d)
    else:
        print("WARNING: Image path not found.")
    return py_images


class ChessPieceImages:
    def __init__(self, dir: str, *args, **kwargs) -> None:
        self.chess_pieces = load_images(dir)
    
