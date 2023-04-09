
import random
import time
from multiprocessing.pool import Pool
from multiprocessing import cpu_count
from functools import partial

from ..base_ai import BaseAI
from ...chess_logic import *

#from ...environment import Environment

BIG_NUMBER = 10000000

class CustomAI(BaseAI):
    def __init__(self, score: ChessScore, max_depth: int = 2, *args, **kwargs) -> None:
        super().__init__(score, *args, **kwargs)
        self.depth = max_depth
        self.mp_start_depth = 10
        self.random_chance = 0.2

    def _sort_move(self, move_tuple: tuple) -> int:
        return -move_tuple[0]

    def _order_move_list(self, board: ChessBoard, board_state: ChessBoardState, moves: list) -> list:
        move_list = []
        move: ChessMove
        for move in moves:

            #Add If taking a piece
            piece_taking: ChessPiece = board_state.piece_board[move.new_position[0] * board.files + move.new_position[1]]
            piece_taking_value = self.score.get_piece_worth(piece_taking)

            #Add if new positions has better bias
            piece_moving: ChessPiece = board_state.piece_board[move.piece.position[0] * board.files + move.piece.position[1]]
            move_difference = self.score.get_position_difference(piece_moving, move.piece.position, move.new_position, board, board_state)

            #Remove if new position can be taken by a pawn
            this_piece_worth = self.score.get_piece_worth(piece_moving)
            pawn_takes_value = 0
            r_diff = -1 if board_state.whites_turn else 1
            r, f = move.new_position[0] + r_diff, move.new_position[1] - 1
            if r >= 0 and r < board.ranks and f >= 0 and f < board.files:
                left_pawn: ChessPiece = board_state.piece_board[r * board.files + f]
                pawn_takes_value = this_piece_worth if left_pawn is not None and left_pawn.is_white != board_state.whites_turn and left_pawn.type == "P" else pawn_takes_value
            r, f = move.new_position[0] + r_diff, move.new_position[1] + 1
            if r >= 0 and r < board.ranks and f >= 0 and f < board.files:
                right_pawn: ChessPiece = board_state.piece_board[r * board.files + f]
                pawn_takes_value = this_piece_worth if right_pawn is not None and right_pawn.is_white != board_state.whites_turn and right_pawn.type == "P" else pawn_takes_value

            #Add all scores together
            score = piece_taking_value + move_difference - pawn_takes_value
            move_list.append((score, move))

        move_list.sort(key=self._sort_move)
        return move_list
    
    def _calc_best_move(self, board: ChessBoard, board_state: ChessBoardState) -> tuple[float, ChessMove]:
        move_list = board_state.white_moves if board_state.whites_turn else board_state.black_moves
        move: ChessMove
        best_score = -BIG_NUMBER if board_state.whites_turn else BIG_NUMBER
        best_move = None
        sorted_list = self._order_move_list(board, board_state, move_list)
        for key, move in sorted_list:
            new_board_state = board.move_piece(move, board_state, True)
            new_score = self.score.calc_score(board, new_board_state)
            if board_state.whites_turn:
                if new_score > best_score:
                    best_score = new_score
                    best_move = move
            else:
                if new_score < best_score:
                    best_score = new_score
                    best_move = move     
        return best_score, best_move    
        
    def _minimax(self, board: ChessBoard, board_state: ChessBoardState, alpha: float = -BIG_NUMBER, beta: float = BIG_NUMBER, depth: int = 0) -> tuple[float, ChessMove]:
        #Depth == 0: Just Check what score each of my moves makes.
        if depth == 0:
            return self._calc_best_move(board, board_state)
        
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
        