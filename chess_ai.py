"""

    Chess Visualizer

"""

import pygame
import random

from chess_ai import *

#Constants
FPS = 60
PIECE_DIR = "./chess_ai/visuals/chess_pieces"

#Declare GlobalState and Global Colors and Pieces
gs = GlobalState()
gc = GlobalColors()
pieces = ChessPieceImages(PIECE_DIR)

## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((gs.w_width, gs.w_height), pygame.RESIZABLE)
pygame.display.set_caption("Chess")
clock = pygame.time.Clock()     ## For syncing the FPS

## Game loop
while gs.running:

    #1 Process input/events

    # will make the loop run at the same speed all the time
    clock.tick(FPS)    

    # gets all the events which have occured till now and keeps tab of them.
    for event in pygame.event.get():        
        check_events(event, gs)

    ########################

    ### Your code comes here

    ########################
    draw_all_shapes(screen, gc, gs)

    ## Done after drawing everything to the screen
    pygame.display.flip()       

pygame.quit()