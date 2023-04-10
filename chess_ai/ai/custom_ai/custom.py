
import random
import time
from multiprocessing.pool import Pool
from multiprocessing import cpu_count
from functools import partial

from ..base_ai import BaseAI
from ...chess_logic import *
from ...minimax import Minimax

#from ...environment import Environment

BIG_NUMBER = 10000000

class CustomAI(BaseAI):
    def __init__(self, score: ChessScore, minimax: Minimax, max_depth: int = 2, *args, **kwargs) -> None:
        super().__init__(score, *args, **kwargs)
        self.depth = max_depth
        self.minimax = minimax
        self.minimax.score = score
        self.mp_start_depth = 10
        self.random_chance = 0.2

    def get_move(self, board: ChessBoard, board_state: ChessBoardState) -> ChessMove | None:
        _, best_move, branches = self.minimax.minimax(board, board_state, depth=self.depth, sorted=True, track_move=True)
        if best_move is not None:
            print(f"Got Best Move: {best_move.piece.position} => {best_move.new_position} in {branches} branches.")
            return best_move
        return None
        