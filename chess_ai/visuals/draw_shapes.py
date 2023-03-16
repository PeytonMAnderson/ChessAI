import pygame

from chess_ai.visuals.global_colors import GlobalColors
from chess_ai.io.global_state import GlobalState

def draw_background(surface: pygame.Surface, global_color: GlobalColors):
    surface.fill(global_color.background)

def draw_board(surface: pygame.Surface, global_color: GlobalColors, global_state: GlobalState):
    white = True
    x, y = global_state.board_origin
    for col in range(global_state.board_dim):

        y = global_state.board_origin[1]
        for row in range(global_state.board_dim):

            if white:
                rect = pygame.Rect(x, y, global_state.square_size, global_state.square_size)
                pygame.draw.rect(surface, global_color.white_square, rect)
            else:
                rect = pygame.Rect(x, y, global_state.square_size, global_state.square_size)
                pygame.draw.rect(surface, global_color.black_square, rect)

            white = False if white else True
            y = y + global_state.square_size

        white = False if white else True
        x = x + global_state.square_size

def draw_all_shapes(surface: pygame.surface, global_color: GlobalColors, global_state: GlobalState):
    draw_background(surface, global_color)
    draw_board(surface, global_color, global_state)


