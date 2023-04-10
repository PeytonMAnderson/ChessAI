
from typing import Callable

from ..chess_logic import *

BIG_NUMBER = 1000000

class Minimax:
    def __init__(self, score: ChessScore, best_score_function: Callable = None, *args, **kwargs) -> None:
        self.score = score
        self.calc_best_score = best_score_function
        if best_score_function is None:
            self.calc_best_score = self._best_score_function

    def _get_best_score(self, best_score: float, best_move: ChessMove, new_score: float, new_move: ChessMove, maximize: bool) -> tuple[float, ChessMove]:
        update = True if (maximize and new_score > best_score) or (not maximize and new_score < best_score) else False
        return (new_score, new_move) if update else (best_score, best_move)
    
    def _best_score_function(self, board: ChessBoard, board_state: ChessBoardState, sorted: bool = True, alpha: float = None, beta: float = None) -> tuple[float, ChessMove]:
        move_list = board_state.white_moves if board_state.whites_turn else board_state.black_moves
        best_score = -BIG_NUMBER if board_state.whites_turn else BIG_NUMBER
        best_move = None
        branches = 0
        move: ChessMove
        for move in move_list:
            branches += 1
            move = move[1] if isinstance(move, tuple) else move
            new_board_state = board.move_piece(move, board_state, True)
            new_score = self.score.calc_score(board, new_board_state)
            best_score, best_move = self._get_best_score(best_score, best_move, new_score, move, board_state.whites_turn)
        if len(move_list) == 0:
            return self.score.calc_score(board, board_state), best_move, branches   
        return best_score, best_move, branches  
    
    def minimax(self, 
                      board: ChessBoard, 
                      board_state: ChessBoardState,  
                      alpha: float = -BIG_NUMBER, 
                      beta: float = BIG_NUMBER, 
                      depth: int = 0,
                      sorted: bool = True,
                      track_move: bool = True
    ) -> tuple[float, ChessMove] | float:
        #Depth == 0: Just Check what score each of my moves makes.
        if depth == 0:
            score, move, branches = self.calc_best_score(board, board_state, True, alpha, beta)
            if track_move:
                return score, move, branches
            return score, branches
        
        #Depth > 0: Recurse to depth == 0
        best_score = -BIG_NUMBER if board_state.whites_turn else BIG_NUMBER
        best_move = None
        branches = 0

        #Sort Moves
        move_list = board_state.white_moves if board_state.whites_turn else board_state.black_moves
        move: ChessPiece
        for move in move_list:
            move = move[1] if isinstance(move, tuple) else move
            new_board_state = board.move_piece(move, board_state, True)
            deep_score, deep_branches = self.minimax(board, new_board_state, alpha, beta, depth - 1, sorted, False)
            best_score, best_move = self._get_best_score(best_score, best_move, deep_score, move, board_state.whites_turn)
            branches += deep_branches

        ret_score = self.score.calc_score(board, board_state) if len(move_list) == 0 else best_score
        if track_move:
            return ret_score, best_move, branches
        return ret_score, branches