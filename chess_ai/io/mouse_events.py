
import pygame

from ..environment import Environment

def mouse_events(event, env: Environment):
    ix, iy = env.io.input_position
    
