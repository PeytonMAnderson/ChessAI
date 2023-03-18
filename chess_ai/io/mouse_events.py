
import pygame

from ..environment import Environment
from ..visuals.draw_shapes import check_bounds
from ..chess_logic.chess_utils import get_piece_on_board, get_is_white
from ..chess_logic.chess_moves import get_valid_moves, move_piece


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
        env.chess.valid_moves = []
    else:
        if env.io.selected_position is None:
            piece = get_piece_on_board(new_selected[0], new_selected[1], env)
            if piece != 0:
                if get_is_white(piece, env.chess.piece_numbers) == env.chess.whites_turn:
                    env.chess.valid_moves = get_valid_moves(new_selected[0], new_selected[1], env)
                    env.io.selected_position = new_selected
        else:
            ro, fo = env.io.selected_position
            rf, ff = new_selected
            #Make sure move is valid
            if env.chess.valid_moves.count(new_selected) != 0:
                if not (ro == rf and fo == ff):
                    move_piece(ro, fo, rf, ff, env)
                    env.io.last_move = new_selected
                env.io.selected_position = None
                env.chess.valid_moves = []

            else:
                #If move is not valid, if move is same as start location, reset move
                if (ro == rf and fo == ff):
                    env.io.selected_position = None
                    env.chess.valid_moves = []
