
import random
import tensorflow as tf
import numpy as np

from ..base_ai import BaseAI
from ...chess_logic import *
from .data import calc_board_arrays, de_normalize

BIG_NUMBER = 1000000

class PolicyAI(BaseAI):
    def __init__(self, score: ChessScore, model_dir_str: str, depth: int = 0, *args, **kwargs):
        super().__init__(score, *args, **kwargs)
        tf.keras.utils.disable_interactive_logging()
        self.model = tf.keras.models.load_model(model_dir_str)
        self.depth = depth

    def _get_boards_arrays(self, board: ChessBoard, board_state: ChessBoardState, move_list: list[ChessMove]) -> list:
        board_arrays_array = []
        move: ChessMove
        for move in move_list:
            new_board_state = board.move_piece(move, board_state, True)
            board_arrays_array.append(calc_board_arrays(board, new_board_state))
        return np.array(board_arrays_array)

    def _predict_best_move(self, board: ChessBoard, board_state: ChessBoardState) -> tuple[float, ChessMove]:
        move_list = board_state.white_moves if board_state.whites_turn else board_state.black_moves
        x_predict = self._get_boards_arrays(board, board_state, move_list)
        if len(move_list) <= 0:
            return None, None
        predict_scores = self.model.predict(x_predict)
        best_score = -BIG_NUMBER if board_state.whites_turn else BIG_NUMBER
        best_move = None
        count = 0
        for score in predict_scores:
            de_score = de_normalize(score[0], self.score)
            if board_state.whites_turn:
                if de_score > best_score:
                    best_score = de_score
                    best_move = move_list[count]
            else:
                if de_score < best_score:
                    best_score = de_score
                    best_move = move_list[count]
            count += 1
        return best_score, best_move
    
    def _minimax(self, board: ChessBoard, board_state: ChessBoardState, alpha: float = -BIG_NUMBER, beta: float = BIG_NUMBER, depth: int = 0) -> tuple[float, ChessMove]:
        #Depth == 0: Just Check what score each of my moves makes.
        if depth == 0:
            return self._predict_best_move(board, board_state)
        
        #Depth > 0: Recurse to depth == 0
        best_score = -BIG_NUMBER if board_state.whites_turn else BIG_NUMBER
        best_move = None
        if board_state.whites_turn:
            #Maximize
            move: ChessPiece
            for move in board_state.white_moves:
                new_board_state = board.move_piece(move, board_state, True)
                deep_score, _ = self._minimax(board, new_board_state, alpha, beta, depth - 1)
                #Max
                if deep_score > best_score:
                    best_score = deep_score
                    best_move = move
                #Alpha
                alpha = max(alpha, best_score)
                #Beta
                if beta <= alpha:
                    break
        else:
            #Maximize
            move: ChessPiece
            for move in board_state.black_moves:
                new_board_state = board.move_piece(move, board_state, True)
                deep_score, _ = self._minimax(board, new_board_state, alpha, beta, depth - 1)
                #Min
                if deep_score < best_score:
                    best_score = deep_score
                    best_move = move
                #Beta
                beta = min(beta, best_score)
                #Alpha
                if beta <= alpha:
                    break
        return best_score, best_move

    def get_move(self, board: ChessBoard, board_state: ChessBoardState) -> ChessMove | None:
        best_score, best_move = self._minimax(board, board_state, depth=self.depth)
        if best_move is not None:
            #print(f"Got Best Move: {best_move.piece.position} => {best_move.new_position} with score of {best_score}")
            return best_move
        return None
        
