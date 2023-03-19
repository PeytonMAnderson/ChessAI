
import pygame

from ..environment import Environment

def keyboard_events(event, env: Environment):
    #Go back in time
    if event.key == pygame.K_LEFT:
        prev_state = env.chess.history.get_previous()
        history_data = env.chess.util.convert_fen_to_board(prev_state['fen_string'], env.chess.board.files, env.chess.board.ranks, env.chess.board.piece_numbers)
        env.chess.board.board = history_data[0]
        env.chess.whites_turn = history_data[1]
        env.chess.state.last_move = prev_state['last_move']

    #Go forward in time
    if event.key == pygame.K_RIGHT:
        next_state = env.chess.history.get_next()
        history_data = env.chess.util.convert_fen_to_board(next_state['fen_string'], env.chess.board.files, env.chess.board.ranks, env.chess.board.piece_numbers)
        env.chess.board.board = history_data[0]
        env.chess.whites_turn = history_data[1]
        env.chess.state.last_move = next_state['last_move']