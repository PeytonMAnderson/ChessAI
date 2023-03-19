
import pygame

from ..environment import Environment
from ..visuals.draw_shapes import check_bounds


def select_square(mouse_position: tuple, env: Environment) -> tuple | None:
    for rank in range(env.chess.board.ranks):
        for file in range(env.chess.board.files):
            if check_bounds(mouse_position, rank, file, env) is True:
                return rank, file
    return None


def mouse_events(event, env: Environment):
    ix, iy = env.io.input_position
    new_selected = select_square((ix, iy), env)
    if new_selected is None:
        env.io.selected_position = None
        env.chess.moves.clear_valid_moves()
    else:
        if env.io.selected_position is None:
            piece = env.chess.util.get_piece_number_on_board(new_selected[0], new_selected[1], env.chess.board.board, env.chess.board.files)
            if piece != 0:
                if env.chess.util.get_is_white_from_piece_number(piece, env.chess.board.piece_numbers) == env.chess.state.whites_turn:
                    env.chess.moves.update_valid_moves(new_selected[0], new_selected[1], env.chess.board.board)
                    env.io.selected_position = new_selected
        else:
            ro, fo = env.io.selected_position
            rf, ff = new_selected
            #Make sure move is valid
            if env.chess.moves.valid_moves_has_move(new_selected):
                if not (ro == rf and fo == ff):
                    env.chess.move_piece(ro, fo, rf, ff)
                    env.io.last_move = new_selected
                env.io.selected_position = None
                env.chess.moves.clear_valid_moves()

            else:
                #If move is not valid, if move is same as start location, reset move
                if (ro == rf and fo == ff):
                    env.io.selected_position = None
                    env.chess.moves.clear_valid_moves()
