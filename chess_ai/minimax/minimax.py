
from typing import Callable

from ..chess_logic import *

BIG_NUMBER = 1000000

class Minimax:
    def __init__(self, score: ChessScore, best_score_function: Callable = None, *args, **kwargs) -> None:
        self.score = score
        self.calc_best_score = best_score_function
        if best_score_function is None:
            self.calc_best_score = self._best_score_function
    
    def _best_score_function(self, board: ChessBoard, board_state: ChessBoardState, sorted: bool = True) -> tuple[float, ChessMove]:
        raise TypeError("Not Implemented Yet.")
    
    def minimax(self, 
                      board: ChessBoard, 
                      board_state: ChessBoardState,  
                      alpha: float = -BIG_NUMBER, 
                      beta: float = BIG_NUMBER, 
                      depth: int = 0,
                      sorted: bool = True,
                      track_move: bool = True
    ) -> tuple[float, ChessMove] | float:
        raise TypeError("Not Implemented Yet.")