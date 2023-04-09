
import random
from ..base_ai import BaseAI
from ...chess_logic import *

class RandomAI(BaseAI):
    def __init__(self, score: ChessScore, *args, **kwargs):
        super().__init__(score, *args, **kwargs)

    def get_move(self, board: ChessBoard, board_state: ChessBoardState) -> ChessMove:
        if board_state.whites_turn:
            move_count = len(board_state.white_moves)
            random_move = random.randint(0, move_count-1)
            return board_state.white_moves[random_move]
        else:
            move_count = len(board_state.black_moves)
            random_move = random.randint(0, move_count-1)
            return board_state.black_moves[random_move]