from ..chess_logic.chess_board import ChessBoard

class BaseAI:
    def __init__(self, is_white: bool, *args, **kwargs):
        self.is_white = is_white
        
    def execute_turn(self, board: ChessBoard, env):
        return