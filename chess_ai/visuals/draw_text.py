from pygame import Surface, Rect, draw, transform, font

from ..environment import Environment
from ..chess_logic.global_chess import get_file_from_number

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

def draw_all_text(surface: Surface, env: Environment):
    draw_ranks_files(surface, env)
