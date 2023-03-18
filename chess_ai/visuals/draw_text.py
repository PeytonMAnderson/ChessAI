from pygame import Surface, Rect, draw, transform, font

from ..environment import Environment
from ..chess_logic.chess_utils import get_file_from_number, get_piece_value
from ..chess_logic.chess_check import check_for_check, check_all_available_moves

def draw_ranks_files(surface: Surface, env: Environment):
    #Get Board Origin
    x0, y0 = env.visual.world_origin
    x_b, y_b = env.visual.board_origin
    size = env.visual.board_square_size * env.visual.zoom
    x, y = x0 + x_b, y0 + y_b
    fontsize = int(env.visual.fontsize_title * env.visual.zoom)
    rf_font = font.Font('freesansbold.ttf', fontsize)

    #Get Rank Origin
    xr, yr =  x - size/2, y + size/4
    for rank in range(env.chess.board_ranks):
        rank_text = rf_font.render(str(env.chess.board_ranks - rank), True, env.visual.fontcolor, env.visual.background_color)
        rank_pos = (xr, yr + size * rank)
        surface.blit(rank_text, rank_pos)

    #Get File Origin
    xf, yf =  x + size/3, y - size/2
    for file in range(env.chess.board_files):
        file_str = get_file_from_number(file)
        file_text = rf_font.render(file_str, True, env.visual.fontcolor, env.visual.background_color)
        file_pos = (xf + size * file, yf)
        surface.blit(file_text, file_pos)

def draw_game_stats(surface: Surface, env: Environment):
    #Get Board Origin
    x0, y0 = env.visual.world_origin
    x_b, y_b = env.visual.board_origin
    size = env.visual.board_square_size * env.visual.zoom
    xo, yo = x0 + x_b, y0 + y_b
    fontsize = int(env.visual.fontsize_title * env.visual.zoom)
    x, y = xo + size * (env.chess.board_files + 1), yo
    rf_font = font.Font('freesansbold.ttf', fontsize)

    #Turn
    turn_text = rf_font.render(f"Turn: {'White' if env.chess.whites_turn else 'Black'}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
    turn_pos = (x, y)

    #Last Move:
    lm_text = rf_font.render(f"Last Move: {env.chess.history[env.chess.history_position][0]}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
    lm_pos = (x, y + fontsize * 2)

    #Check Status
    check_status = "None"

    white_king = get_piece_value('K', env.chess.piece_numbers)
    black_king = get_piece_value('k', env.chess.piece_numbers)

    white_check = check_for_check(white_king, env.chess.board, env)
    black_check = check_for_check(black_king, env.chess.board, env)

    white_moves = check_all_available_moves(True, env.chess.board, env)
    black_moves = check_all_available_moves(False, env.chess.board, env)

    if white_check:
        if len(white_moves) == 0:
            check_status = "Black Checkmate"
        else:
            check_status = "Black Check"
    elif black_check:
        if len(black_moves) == 0:
            check_status = "White Checkmate"
        else:
            check_status = "White Check"
    else:
        if env.chess.whites_turn and len(white_moves) == 0:
            check_status = "Black Stalemate"
        elif not env.chess.whites_turn and len(black_moves) == 0:
            check_status = "White Stalemate"
        else:
            "None"

    check_text = rf_font.render(f"Check: {check_status}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
    check_pos = (x, y + fontsize * 4)

    #Blit
    surface.blit(turn_text, turn_pos)
    surface.blit(lm_text, lm_pos)
    surface.blit(check_text, check_pos)   

def draw_all_text(surface: Surface, env: Environment):
    draw_ranks_files(surface, env)
    draw_game_stats(surface, env)
