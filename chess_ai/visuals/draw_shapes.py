from pygame import Surface, Rect, draw, transform

from ..environment import Environment
from .images import get_image_from_number
from .draw_text import draw_score_text

def draw_background(surface: Surface, env: Environment):
    surface.fill(env.visual.background_color)


def get_local_board_coords(env: Environment):
    #Get Pieces Origin
    x0, y0 = env.visual.world_origin
    x_b, y_b = env.visual.board_origin
    size = env.visual.board_square_size * env.visual.zoom
    x_o, y_o = x0 + x_b, y0 + y_b
    return x_o, y_o, size

def draw_board(surface: Surface, env: Environment):
    white = False
    x, yo, size = get_local_board_coords(env)
    for file in range(env.chess.board.files):
        y = yo
        for rank in range(env.chess.board.ranks):

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
    rank_index_per = 0 if env.visual.perspective == "WHITE" else env.chess.board.ranks - 1
    file_index_per = 0 if env.visual.perspective == "WHITE" else env.chess.board.files - 1
    per_diff = 1 if env.visual.perspective == "WHITE" else -1

    x, y, size = get_local_board_coords(env)

    while rank_index < env.chess.board.ranks:
        file_index = 0
        file_index_per = 0 if env.visual.perspective == "WHITE" else env.chess.board.files - 1
        while file_index < env.chess.board.files:

            #Get place image from chess board
            num = env.chess.board.board[rank_index * env.chess.board.files + file_index]
            img = get_image_from_number(num, env)
            if img is not None:
                #Get Size of Piece
                size = env.visual.board_square_size * env.visual.zoom
                #Get Position of Piece
                img_x = x + file_index_per * size
                img_y = y + rank_index_per * size
                #Scale and place image on canvas
                img = transform.scale(img, (size, size))
                surface.blit(img, (img_x, img_y))

            file_index += 1
            file_index_per += per_diff
        rank_index_per += per_diff
        rank_index += 1

def draw_square_from_position(surface: Surface, rank_i: int, file_i:int, color: tuple, env: Environment) -> None:
    rd, fd = env.visual.adjust_perspective(rank_i, file_i, env)
    x_o, y_o, size = get_local_board_coords(env)
    x, y = x_o + fd * size, y_o + rd * size
    rect = Rect(x, y, size, size)
    draw.rect(surface, color, rect)

def check_bounds(mouse_position: tuple, rank_i: int, file_i: int, env: Environment) -> bool:
    x_o, y_o, size = get_local_board_coords(env)

    #Get Piece Position
    x, y = x_o + file_i * size, y_o + rank_i * size
    xf, yf = x + size, y + size

    #Get Mouse Position
    mx, my = mouse_position

    if (mx >= x and mx <= xf):
        if (my >= y and my <= yf):
            return True
    return False

def draw_selected(surface: Surface, env: Environment):
    x_o, y_o, size = get_local_board_coords(env)
    if env.io.selected_position is not None:
        rd, fd = env.visual.adjust_perspective(env.io.selected_position[0], env.io.selected_position[1], env)
        x, y = x_o + fd * size, y_o + rd * size
        rect = Rect(x, y, size, size)
        draw.rect(surface, env.visual.board_selected_color, rect)

def grab_selected(surface: Surface, env: Environment):
    if env.io.selected_position is not None:
        piece = env.chess.util.get_piece_number_on_board(env.io.selected_position[0], env.io.selected_position[1], env.chess.board.board, env.chess.board.files)
        if piece is not None and piece != 0:
            img = get_image_from_number(piece, env)
            if img is not None:
                #Get Size of Piece
                size = env.visual.board_square_size * env.visual.zoom
                #Get Position of Piece
                img_x, img_y = env.io.input_position
                img_x, img_y = img_x - size /2, img_y - size /2
                #Scale and place image on canvas
                img = transform.scale(img, (size, size))
                surface.blit(img, (img_x, img_y))

def draw_valid_moves(surface: Surface, env: Environment):
    x_o, y_o, size = get_local_board_coords(env)
    for valid_move in env.chess.moves.get_valid_moves_list():
        rank_o, file_o, rank, file = valid_move
        rd, fd = env.visual.adjust_perspective(rank, file, env)
        x, y = x_o + fd * size, y_o + rd * size
        rect = Rect(x, y, size, size)
        draw.rect(surface, env.visual.board_valid_moves_color, rect)

def draw_last_move(surface: Surface, env: Environment):
    if env.chess.state.last_move_tuple is not None:
        ro, fo, rf, ff = env.chess.state.last_move_tuple
        draw_square_from_position(surface, ro, fo, env.visual.board_last_move_from_color, env)
        draw_square_from_position(surface, rf, ff, env.visual.board_last_move_to_color, env)

def draw_score_bar(surface: Surface, env: Environment):
    x_o, y_o, size = get_local_board_coords(env)
    x, y = x_o, y_o + size * env.chess.board.ranks + size/2
    bar_size = size * env.chess.board.files
    white_rect = Rect(x, y, bar_size, size/2)
    draw.rect(surface, env.visual.colors['WHITE'], white_rect)

    score_diff = env.chess.score.score
    score_total = env.chess.score.score_max
    score_black = score_total - score_diff
    score_ratio = score_black / (score_total * 2)
    if -score_diff > score_total:
        score_ratio = 1.0
    black_size = score_ratio * bar_size
    black_rect = Rect(x, y, black_size, size/2)
    draw.rect(surface, env.visual.colors['GRAY'], black_rect)
    draw_score_text(surface, x + black_size, y, score_diff, size/2, env)


def draw_all_shapes(surface: Surface, env: Environment):
    #Draw Background
    draw_background(surface, env)

    #Draw Board and highlighting
    draw_board(surface, env)
    draw_selected(surface, env)
    draw_last_move(surface, env)
    draw_valid_moves(surface, env)

    #Draw Score Bar
    draw_score_bar(surface, env)

    #Draw pieces sprites
    draw_pieces(surface, env)

    #Draw piece attached to mouse
    grab_selected(surface, env)
    


