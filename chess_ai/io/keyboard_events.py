
import pygame

#from ..environment import Environment

class KeyboardEvents:
    def __init__(self, *args, **kwargs) -> None:
        """Event Handler for keyboard events.
        """
        pass

    def _key_history(self, event, env):
        """Gets the keys for history.

        Args:
            event (_type_): Event Object (Includes which key press).
            env (Environment): The environment.
        """
        #Go back in time
        if event.key == pygame.K_LEFT:
            env.ai.paused = True
            prev_state = env.chess.history.get_previous()
            env.chess.load_from_history(prev_state, env)

        #Go forward in time
        if event.key == pygame.K_RIGHT:
            env.ai.paused = True
            next_state = env.chess.history.get_next()
            env.chess.load_from_history(next_state, env)

        #Unpause / Pause AI
        if event.key == pygame.K_SPACE:
            env.ai.paused = False if env.ai.paused else True

    def keyboard_events(self, event, env):
        """Listen for keyboard actions. Updates Environment.

        Args:
            event (any): The event object.
            env (Environment): The environment.
        """
        self._key_history(event, env)
