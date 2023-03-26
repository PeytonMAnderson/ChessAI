
import pygame

#from ..environment import Environment
from ..chess_logic.chess_piece import ChessPiece
from ..chess_logic.chess_move import ChessMove

class MouseEvents:
    def __init__(self, *args, **kwargs) -> None:
        """Event Handler for mouse events.
        """
        self.mouse_down = False
        self.original_position = (0,0)
        self.old_world_origin = (0,0)

    def _get_move(self, old_selected: tuple, new_selected: tuple, env) -> ChessMove | None:
        """Get the move from the list of available moves if they match the old_selected and new_selected positions.

        Args:
            old_selected (tuple): The original position of the piece.
            new_selected (tuple): The new position of the piece.
            env (Environment): The environment.

        Returns:
            ChessMove | None: The Move that matches the old and new positions.
        """
        move: ChessMove
        if env.chess.board.state.whites_turn:
            for move in env.chess.board.state.white_moves:
                if move.new_position == new_selected and move.piece.position == old_selected:
                    return move
        else:
            for move in env.chess.board.state.black_moves:
                if move.new_position == new_selected and move.piece.position == old_selected:
                    return move
        return None

    def _mouse_left_click_events(self, event: any, env):
        """Listen for mouse left click and perform actions. Updates Environment.

        Args:
            event (any): The event object.
            env (Environment): The environment.
        """
        ix, iy = env.io.input_position
        new_selected = env.visual.shapes._select_square(env.io.input_position, env)
        if new_selected is None:
            env.io.selected_position = None
        else:
            if env.io.selected_position is None:
                piece: ChessPiece = env.chess.board.state.piece_board[new_selected[0] * env.chess.board.files + new_selected[1]]
                if piece is not None:
                    if piece.is_white == env.chess.board.state.whites_turn and env.ai.piece_is_playable(piece.is_white):
                        env.io.selected_position = new_selected
            elif env.io.selected_position != new_selected:

                new_move = self._get_move(env.io.selected_position, new_selected, env)
                if new_move is not None:
                    env.ai.paused = False
                    env.chess.move_piece(new_move, env)
                    env.io.selected_position = None
            else:
                env.io.selected_position = None

    def mouse_events(self, event, mouse_down: bool, env):
        """Listen for all mouse events. Updates env.

        Args:
            event (_type_): The event object.
            env (Environment): The environment.
        """
        if event.button == 1 and mouse_down:
            self._mouse_left_click_events(event, env)
        if mouse_down:
            self.mouse_down = True
            self.original_position = env.io.input_position
            self.old_world_origin = env.visual.world_origin
        else:
            self.mouse_down = False

    def scroll_event(self, event, env):
        ratio_minus = round(1 - env.io.zoom_speed, 3)
        ratio_plus = round(1 + env.io.zoom_speed, 3)
        if event.y < 0:
            old_zoom = env.visual.zoom
            new_zoom = env.visual.zoom * ratio_minus
            env.visual.zoom = new_zoom

            xw, yw = env.visual.world_origin[0], env.visual.world_origin[1]
            xo, yo = xw + env.io.input_position[0] * old_zoom, yw + env.io.input_position[1] * old_zoom
            xf, yf = xw + env.io.input_position[0] * new_zoom, yw + env.io.input_position[1] * new_zoom
            xd, yd = int(xf - xo), int(yf - yo)
            env.visual.world_origin = xw - xd * (1/ratio_minus), yw
            print(f"{env.io.input_position}, {xo, yo} -> {xf, yf} ({xd, yd}) = {xf - xd, yf - yd}")

        elif event.y > 0:
            old_zoom = env.visual.zoom
            new_zoom = env.visual.zoom * ratio_plus
            env.visual.zoom = new_zoom
            
            xw, yw = env.visual.world_origin[0], env.visual.world_origin[1]
            xo, yo = xw + env.io.input_position[0] * old_zoom, yw + env.io.input_position[1] * old_zoom
            xf, yf = xw + env.io.input_position[0] * new_zoom, yw + env.io.input_position[1] * new_zoom
            xd, yd = xf - xo, yf - yo
            env.visual.world_origin = int(xw - xd * (1/ratio_plus)), yw
            print(f"{env.io.input_position}, {xo, yo} -> {xf, yf} ({xd, yd}) = {int(xf - xd), int(yf - yd)}")
            

