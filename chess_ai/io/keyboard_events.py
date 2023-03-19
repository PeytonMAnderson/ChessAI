
import pygame

from ..environment import Environment

def keyboard_events(event, env: Environment):
    #Go back in time
    if event.key == pygame.K_LEFT:
        prev_state = env.chess.history.get_previous()
        env.chess.load_from_history(prev_state)

    #Go forward in time
    if event.key == pygame.K_RIGHT:
        next_state = env.chess.history.get_next()
        env.chess.load_from_history(next_state)