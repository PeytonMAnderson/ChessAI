
import random
from ..base_ai import BaseAI
from ...chess_logic.chess_board import ChessBoard

class RandomAI(BaseAI):
    def __init__(self, is_white: bool, *args, **kwargs):
        super().__init__(is_white, *args, **kwargs)
        
    def execute_turn(self, board: ChessBoard, env):
        if self.is_white:
            move_count = len(board.state.white_moves)
            random_move = random.randint(0, move_count-1)
            env.chess.move_piece(board.state.white_moves[random_move], env)
        else:
            move_count = len(board.state.black_moves)
            random_move = random.randint(0, move_count-1)
            env.chess.move_piece(board.state.black_moves[random_move], env)