from ..chess_logic.chess_board import ChessBoard
from ..chess_logic.chess_move import ChessMove

class BaseAI:
    def __init__(self, is_white: bool, *args, **kwargs):
        self.is_white = is_white

    def get_move(self, board: ChessBoard, env = None) -> ChessMove:
        raise TypeError("Not Implemented Yet.")
        
    def execute_turn(self, board: ChessBoard, env = None) -> None:
        raise TypeError("Not Implemented Yet.")