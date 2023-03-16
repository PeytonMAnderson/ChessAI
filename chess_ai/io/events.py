import pygame

from chess_ai.io.global_state import GlobalState

def check_events(event, global_state: GlobalState):
    ## listening for the the X button at the top
    if event.type == pygame.QUIT:
        global_state.running = False
    
    if event.type == pygame.VIDEORESIZE:
        global_state.w_width = event.w
        global_state.w_height = event.h