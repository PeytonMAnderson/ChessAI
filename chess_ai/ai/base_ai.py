from ..chess_logic.chess_board import ChessBoard, ChessBoardState
from ..chess_logic.chess_move import ChessMove

class BaseAI:
    def __init__(self, *args, **kwargs):
        pass
    def get_move(self, board: ChessBoard, board_state: ChessBoardState, env = None) -> ChessMove:
        raise TypeError("Not Implemented Yet.")
    def execute_turn(self, board: ChessBoard, env = None) -> None:
        raise TypeError("Not Implemented Yet.")