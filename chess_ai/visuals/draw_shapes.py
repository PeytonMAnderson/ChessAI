from pygame import Surface, Rect, draw, transform

from ..environment import Environment
from .images import get_image_from_number

def draw_background(surface: Surface, env: Environment):
    surface.fill(env.visual.background_color)

def draw_board(surface: Surface, env: Environment):
    white = True

    x0, y0 = env.visual.world_origin
    x_b, y_b = env.visual.board_origin
    x, y = x0 + x_b, y0 + y_b

    size = env.visual.board_square_size * env.visual.zoom

    for file in range(env.chess.board_files):

        y = y0 + y_b
        for rank in range(env.chess.board_ranks):

            if white:
                rect = Rect(x, y, size, size)
                draw.rect(surface, env.visual.board_white_color, rect)
            else:
                rect = Rect(x, y, size, size)
                draw.rect(surface, env.visual.board_black_color, rect)

            white = False if white else True
            y = y + size

        white = False if white else True
        x = x + size

def draw_pieces(surface: Surface, env: Environment):
    rank_index = 0
    file_index = 0

    x0, y0 = env.visual.world_origin
    x_b, y_b = env.visual.board_origin
    x, y = x0 + x_b, y0 + y_b

    while rank_index < env.chess.board_ranks:
        file_index = 0
        while file_index < env.chess.board_files:

            #Get place image from chess board
            num = env.chess.board[rank_index * env.chess.board_files + file_index]
            img = get_image_from_number(num, env)
            if img is not None:
                #Get Size of Piece
                size = env.visual.board_square_size * env.visual.zoom
                #Get Position of Piece
                img_x = x + file_index * size
                img_y = y + rank_index * size
                #Scale and place image on canvas
                img = transform.scale(img, (size, size))
                surface.blit(img, (img_x, img_y))

            file_index += 1
        rank_index += 1


def draw_all_shapes(surface: Surface, env: Environment):
    draw_background(surface, env)
    draw_board(surface, env)
    draw_pieces(surface, env)


