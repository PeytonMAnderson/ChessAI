"""

    Chess Visualizer

"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import random

from chess_ai import *

#Constants
FPS = 60
PIECES_DIR = "./chess_ai/visuals/chess_pieces"
ICONS_DIR = "./chess_ai/visuals/icons"
SOUNDS_DIR = "./chess_ai/sounds/chess_sounds"
CONFIG_FILE = "./chess_config.yaml"

import socketio
from time import sleep # just used for timing the messages

sio = socketio.Client()

@sio.event
def connect():
    print('Connection established with server to send message data.')

def send_msg(msg):
    print("sending")
    sio.emit('msg', msg)

@sio.event
def disconnect():
    print('Disconnected from websocket! Cannot send message data.')

sio.connect('ws://192.168.1.22:8800')

# list of messages to send
MESSAGE_LIST = ["66903222854465",
                "36558352171508",
                "42493680134299",
                "32010903761366",
                "37556732408598",
                "00418984412935",
                "54555467232969",
                "95461295964563",
                "63543734057786",
                "37925062203941"]

# logic to send the 10 messages then close connection
x = 0
while x < 10:
    send_msg(MESSAGE_LIST[x])
    sleep(1)
    x += 1

sio.disconnect()


def main():

    ## initialize pygame and create window
    pygame.init()
    pygame.mixer.init()  ## For sound

    #Declare GlobalState and Global Colors and Pieces
    env = Environment(CONFIG_FILE, PIECES_DIR, ICONS_DIR, SOUNDS_DIR)

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
            env.io.events.check_events(event, env)       

        ########################

        ### Your code comes here

        ########################
        env.visual.shapes.draw_all_shapes(screen, env)
        env.visual.text.draw_all_text(screen, env)
        env.execute_next_turn()
        
        ## Done after drawing everything to the screen
        pygame.display.flip()       

    pygame.quit()

if __name__ == "__main__":
    main()