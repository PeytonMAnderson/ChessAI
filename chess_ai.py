"""

    Chess Visualizer

"""

import pygame
import random

from chess_ai import *

#Constants
FPS = 60
PIECES_DIR = "./chess_ai/visuals/chess_pieces"
CONFIG_FILE = "./chess_config.yaml"

#Declare GlobalState and Global Colors and Pieces
env = Environment(CONFIG_FILE, PIECES_DIR)

## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((env.visual.w_width, env.visual.w_height), pygame.RESIZABLE)
pygame.display.set_caption("Chess")
clock = pygame.time.Clock()     ## For syncing the FPS

## Game loop
while env.io.running:

    #1 Process input/events

    # will make the loop run at the same speed all the time
    clock.tick(FPS)    

    # gets all the events which have occured till now and keeps tab of them.
    for event in pygame.event.get():        
        check_events(event, env)

    ########################

    ### Your code comes here

    ########################
    draw_all_shapes(screen, env)
    

    ## Done after drawing everything to the screen
    pygame.display.flip()       

pygame.quit()