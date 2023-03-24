
import pygame

#from ..environment import Environment
from ..chess_logic.chess_piece import ChessPiece
from ..chess_logic.chess_move import ChessMove

class MouseEvents:
    def __init__(self, *args, **kwargs) -> None:
        """Event Handler for mouse events.
        """
        pass

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
        if env.chess.board.whites_turn:
            for move in env.chess.board.white_moves:
                if move.new_position == new_selected and move.piece.position == old_selected:
                    return move
        else:
            for move in env.chess.board.black_moves:
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
                piece: ChessPiece = env.chess.board.piece_board[new_selected[0] * env.chess.board.files + new_selected[1]]
                if piece is not None:
                    if piece.is_white == env.chess.board.whites_turn and env.ai.piece_is_playable(piece.is_white):
                        env.io.selected_position = new_selected
            elif env.io.selected_position != new_selected:

                new_move = self._get_move(env.io.selected_position, new_selected, env)
                if new_move is not None:
                    env.ai.paused = False
                    env.chess.move_piece(new_move, env)
                    env.io.selected_position = None
            else:
                env.io.selected_position = None

    def mouse_events(self, event, env):
        """Listen for all mouse events. Updates env.

        Args:
            event (_type_): The event object.
            env (Environment): The environment.
        """
        if event.button == 1:
            self._mouse_left_click_events(event, env)

