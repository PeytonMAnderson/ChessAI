
import pygame

from ..environment import Environment
from ..chess_logic.global_chess import convert_fen_to_board
from ..chess_logic.chess_utils import get_position_from_move_str

def keyboard_events(event, env: Environment):
    #Go back in time
    if event.key == pygame.K_LEFT:
        if env.chess.history_position > 0:
            env.chess.history_position -= 1
        last_move = env.chess.history[env.chess.history_position][0]
        board = env.chess.history[env.chess.history_position][1]
        history_data = convert_fen_to_board(board, env.chess.board_files, env.chess.board_ranks, env.chess.piece_numbers)
        env.chess.board = history_data[0]
        env.chess.whites_turn = history_data[1]
        env.io.last_move = get_position_from_move_str(last_move, env)

    #Go forward in time
    if event.key == pygame.K_RIGHT:
        if env.chess.history_position < len(env.chess.history) - 1:
            env.chess.history_position += 1
        last_move = env.chess.history[env.chess.history_position][0]
        board = env.chess.history[env.chess.history_position][1]
        history_data = convert_fen_to_board(board, env.chess.board_files, env.chess.board_ranks, env.chess.piece_numbers)
        env.chess.board = history_data[0]
        env.chess.whites_turn = history_data[1]
        env.io.last_move = get_position_from_move_str(last_move, env)