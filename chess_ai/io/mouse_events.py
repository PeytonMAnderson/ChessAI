
import pygame

from ..environment import Environment
from ..visuals.draw_shapes import check_bounds


def select_square(mouse_position: tuple, env: Environment) -> tuple | None:
    for rank in range(env.chess.board.ranks):
        for file in range(env.chess.board.files):
            if check_bounds(mouse_position, rank, file, env) is True:
                return rank, file
    return None

def mouse_left_click_events(event, env: Environment):
    ix, iy = env.io.input_position
    new_selected = select_square((ix, iy), env)
    if new_selected is None:
        env.io.selected_position = None
        env.chess.moves.clear_valid_moves()
    else:
        if env.io.selected_position is None:
            piece_value = env.chess.util.get_piece_number_on_board(new_selected[0], new_selected[1], env.chess.board.board, env.chess.board.files)
            if piece_value != 0:
                is_white = env.chess.util.get_is_white_from_piece_number(piece_value, env.chess.board.piece_numbers)
                if is_white == env.chess.state.whites_turn and env.ai.piece_is_playable(is_white):
                    env.chess.moves.update_valid_moves(new_selected[0], new_selected[1], env.chess.board.board, env.chess.state.castle_avail, env.chess.state.en_passant, env.chess.state.whites_turn)
                    env.io.selected_position = new_selected
        else:
            ro, fo = env.io.selected_position
            rf, ff = new_selected
            #Make sure move is valid
            if env.chess.moves.valid_moves_has_move(env.io.selected_position[0], env.io.selected_position[1], rf, ff):
                if not (ro == rf and fo == ff):
                    env.ai.paused = False
                    env.chess.move_piece(ro, fo, rf, ff)
                    env.io.last_move = new_selected
                env.io.selected_position = None
                env.chess.moves.clear_valid_moves()

            else:
                #If move is not valid, if move is same as start location, reset move
                if (ro == rf and fo == ff):
                    env.io.selected_position = None
                    env.chess.moves.clear_valid_moves()

def mouse_events(event, env: Environment):
    if event.button == 1:
        mouse_left_click_events(event, env)

