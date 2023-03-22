import pygame

from ..environment import Environment
from .mouse_events import MouseEvents
from .keyboard_events import KeyboardEvents

class Events:
    def __init__(self, *args, **kwargs) -> None:
        self.keyboard = KeyboardEvents()
        self.mouse = MouseEvents()

    def check_events(self, event: any, env: Environment):
        """Checks for ALL events and updates env.

        Args:
            event (any): Event Oject.
            env (Environment): The environment.
        """
        ## listening for the the X button at the top
        if event.type == pygame.QUIT:
            env.io.running = False
        
        if event.type == pygame.VIDEORESIZE:
            env.visual.w_width = event.w
            env.visual.w_height = event.h

        if event.type == pygame.MOUSEWHEEL:

            ratio_minus = round(1 - env.io.zoom_speed, 3)
            ratio_plus = round(1 + env.io.zoom_speed, 3)

            if event.y < 0:
                env.visual.zoom = env.visual.zoom * ratio_minus
            elif event.y > 0:
                env.visual.zoom = env.visual.zoom * ratio_plus
        
        if event.type == pygame.MOUSEMOTION:
            env.io.input_position = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse.mouse_events(event, env)
        
        if event.type == pygame.KEYDOWN:
            self.keyboard.keyboard_events(event, env)
