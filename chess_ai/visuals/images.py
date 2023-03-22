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

def get_image_from_number(number: int, env):
    #See if number is a piece
    if number == 0:
        return None
    
    #Get Color of Piece
    img_str = ""
    if int(number / 10) == env.chess.board.utils.piece_values.get("WHITE"):
        img_str =  "w"
    elif int(number / 10) == env.chess.board.utils.piece_values.get("BLACK"):
        img_str = "b"

    #Get Type of Piece
    img_str = img_str + "_"
    if number % 10 == env.chess.board.utils.piece_values.get("PAWN"):
        return env.piece_images[img_str + 'p']
    elif number % 10 == env.chess.board.utils.piece_values.get("KNIGHT"):
        return env.piece_images[img_str + 'n']
    elif number % 10 == env.chess.board.utils.piece_values.get("BISHOP"):
        return env.piece_images[img_str + 'b']
    elif number % 10 == env.chess.board.utils.piece_values.get("ROOK"):
        return env.piece_images[img_str + 'r']
    elif number % 10 == env.chess.board.utils.piece_values.get("QUEEN"):
        return env.piece_images[img_str + 'q']
    elif number % 10 == env.chess.board.utils.piece_values.get("KING"):
        return env.piece_images[img_str + 'k']
    else:
        print("WARNING: Piece does not exist.")




    
