
import pygame

from ..environment import Environment
from ..chess_logic.global_chess import convert_fen_to_board

def keyboard_events(event, env: Environment):
    #Go back in time
    if event.key == pygame.K_LEFT:
        if env.chess.history_position > 0:
            env.chess.history_position -= 1
        board = env.chess.history[env.chess.history_position][1]
        env.chess.board = convert_fen_to_board(board, env.chess.board_files, env.chess.board_ranks, env.chess.piece_numbers)

    #Go forward in time
    if event.key == pygame.K_RIGHT:
        if env.chess.history_position < len(env.chess.history) - 1:
            env.chess.history_position += 1
        board = env.chess.history[env.chess.history_position][1]
        env.chess.board = convert_fen_to_board(board, env.chess.board_files, env.chess.board_ranks, env.chess.piece_numbers)