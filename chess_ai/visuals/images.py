import pygame
import os

from ..chess_logic.chess_piece import ChessPiece

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

def get_image_from_piece(piece: ChessPiece, env) -> any:
    if isinstance(piece, ChessPiece):
        img_str = "w" if piece.is_white else "b"
        img_str += "_"
        img_str += piece.type.lower()
        return env.piece_images[img_str]
    raise TypeError(f"Piece cannot be of type {piece}.")




    
