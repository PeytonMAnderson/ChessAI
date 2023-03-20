
import pygame

from ..environment import Environment

def keyboard_events(event, env: Environment):
    #Go back in time
    if event.key == pygame.K_LEFT:
        env.ai.paused = True
        prev_state = env.chess.history.get_previous()
        env.chess.load_from_history(prev_state)
        env.chess.score.update_score(env.chess.board.board)

    #Go forward in time
    if event.key == pygame.K_RIGHT:
        env.ai.paused = True
        next_state = env.chess.history.get_next()
        env.chess.load_from_history(next_state)
        env.chess.score.update_score(env.chess.board.board)