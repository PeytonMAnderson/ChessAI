from pygame import Surface, Rect, draw, transform, font

from ..environment import Environment

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
    for rank in range(env.chess.board.ranks):
        rank_str = env.chess.util.get_rank_from_number(rank, env.chess.board.ranks)
        rank_text = rf_font.render(rank_str, True, env.visual.fontcolor, env.visual.background_color)
        rank_pos = (xr, yr + size * rank)
        surface.blit(rank_text, rank_pos)

    #Get File Origin
    xf, yf =  x + size/3, y - size/2
    for file in range(env.chess.board.files):
        file_str = env.chess.util.get_file_from_number(file)
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
    x, y = xo + size * (env.chess.board.files + 1), yo
    rf_font = font.Font('freesansbold.ttf', fontsize)

    #Turn
    turn_text = rf_font.render(f"Turn: {'White' if env.chess.state.whites_turn else 'Black'}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
    turn_pos = (x, y)

    #Last Move:
    lm_text = rf_font.render(f"Last Move: {env.chess.state.last_move_str}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
    lm_pos = (x, y + fontsize * 2)

    #Check Status
    check_text = rf_font.render(f"Check: {env.chess.state.check_status}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
    check_pos = (x, y + fontsize * 4)

    #Blit
    surface.blit(turn_text, turn_pos)
    surface.blit(lm_text, lm_pos)
    surface.blit(check_text, check_pos)   

def draw_all_text(surface: Surface, env: Environment):
    draw_ranks_files(surface, env)
    draw_game_stats(surface, env)
