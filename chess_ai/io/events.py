import pygame

from .mouse_events import MouseEvents
from .keyboard_events import KeyboardEvents
#from ..environment import Environment

class Events:
    def __init__(self, *args, **kwargs) -> None:
        """Event Handler for Keyboard, Mouse, etc.
        """
        self.keyboard = KeyboardEvents()
        self.mouse = MouseEvents()

    def check_events(self, event: any, env):
        """Checks for ALL events and updates env.

        Args:
            event (any): Event Oject.
            env (Environment): The environment.
        """
        ## listening for the the X button at the top
        if event.type == pygame.QUIT:
            env.io.running = False
        
        #Screen Resize
        if event.type == pygame.VIDEORESIZE:
            env.visual.w_width = event.w
            env.visual.w_height = event.h

        #Mouse Events
        if event.type == pygame.MOUSEWHEEL:
            self.mouse.scroll_event(event, env)
        if event.type == pygame.MOUSEMOTION:
            env.io.input_position = pygame.mouse.get_pos()
            if self.mouse.mouse_down and env.io.selected_position is None:
                xd, yd = env.io.input_position[0] - self.mouse.original_position[0], env.io.input_position[1] - self.mouse.original_position[1]
                env.visual.world_origin = self.mouse.old_world_origin[0] + xd, self.mouse.old_world_origin[1] + yd
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse.mouse_events(event, True, env)
        if event.type == pygame.MOUSEBUTTONUP:
            self.mouse.mouse_events(event, False, env)
        #Keyboard Events
        if event.type == pygame.KEYDOWN:
            self.keyboard.keyboard_events(event, env)
        
