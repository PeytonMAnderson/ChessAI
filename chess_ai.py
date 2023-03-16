"""

    Chess Visualizer

"""

import pygame
import random

#Constants
WIDTH = 1280
HEIGHT = 720
FPS = 60

# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 125, 0)
YELLOW = (255, 225, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)
MAGENTA = (255, 0, 125)

## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Chess")
clock = pygame.time.Clock()     ## For syncing the FPS


## group all the sprites together for ease of update
all_sprites = pygame.sprite.Group()

#Global Variables
w_width = WIDTH
w_height = HEIGHT




## Game loop
running = True
while running:

    #1 Process input/events
    clock.tick(FPS)     ## will make the loop run at the same speed all the time
    for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them.
        ## listening for the the X button at the top
        if event.type == pygame.QUIT:
            running = False


    #2 Update
    all_sprites.update()


    #3 Draw/render
    screen.fill(BLACK)

    

    all_sprites.draw(screen)
    ########################

    ### Your code comes here

    ########################

    ## Done after drawing everything to the screen
    pygame.display.flip()       

pygame.quit()