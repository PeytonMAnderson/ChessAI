
import pygame

from ..environment import Environment
from ..visuals.draw_shapes import check_bounds
from ..chess_logic.global_chess import get_piece_on_board, move_piece


def select_square(mouse_position: tuple, env: Environment) -> tuple | None:
    for rank in range(env.chess.board_ranks):
        for file in range(env.chess.board_files):
            if check_bounds(mouse_position, rank, file, env) is True:
                return rank, file
    return None


def mouse_events(event, env: Environment):
    ix, iy = env.io.input_position
    new_selected = select_square((ix, iy), env)
    if new_selected is None:
        env.io.selected_position = None
    else:
        if env.io.selected_position is None:
            if get_piece_on_board(new_selected[0], new_selected[1], env) != 0:
                env.io.selected_position = new_selected
        else:
            ro, fo = env.io.selected_position
            rf, ff = new_selected
            if not (ro == rf and fo == ff):
                move_piece(ro, fo, rf, ff, env)
                env.io.last_move = new_selected
            env.io.selected_position = None

