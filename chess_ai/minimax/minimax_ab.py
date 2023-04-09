from typing import Callable

from ..chess_logic import *
from .minimax import Minimax

BIG_NUMBER = 1000000

class MinimaxAlphaBeta(Minimax):
    def __init__(self, score: ChessScore, best_score_function: Callable = None, *args, **kwargs) -> None:
        calc_best_score = best_score_function
        if best_score_function is None:
            calc_best_score = self._best_score_function
        super().__init__(score, calc_best_score, *args, **kwargs)

    def _best_score_function(self, board: ChessBoard, board_state: ChessBoardState, sorted: bool = True) -> tuple[float, ChessMove]:
        move_list = board_state.white_moves if board_state.whites_turn else board_state.black_moves
        sorted_list = move_list if not sorted else self._order_move_list(board, board_state, move_list)
        best_score = -BIG_NUMBER if board_state.whites_turn else BIG_NUMBER
        best_move = None
        move: ChessMove
        for move in sorted_list:
            move = move[1] if isinstance(move, tuple) else move
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
        if len(sorted_list) == 0:
            return self.score.calc_score(board, board_state), best_move
        return best_score, best_move    

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
            score, move = self.calc_best_score(board, board_state)
            if track_move:
                return score, move
            return score
        
        #Depth > 0: Recurse to depth == 0
        best_score = -BIG_NUMBER if board_state.whites_turn else BIG_NUMBER
        best_move = None

        if board_state.whites_turn:
            #Maximize
            move: ChessPiece
            sorted_list = board_state.white_moves if not sorted else self._order_move_list(board, board_state, board_state.white_moves)
            for move in sorted_list:
                move = move[1] if isinstance(move, tuple) else move
                new_board_state = board.move_piece(move, board_state, True)
                deep_score = self.minimax(board, new_board_state, alpha, beta, depth - 1, sorted, False)
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
            sorted_list = board_state.white_moves if not sorted else self._order_move_list(board, board_state, board_state.black_moves)
            for move in sorted_list:
                move = move[1] if isinstance(move, tuple) else move
                new_board_state = board.move_piece(move, board_state, True)
                deep_score = self.minimax(board, new_board_state, alpha, beta, depth - 1, sorted, False)
                #Min
                if deep_score < best_score:
                    best_score = deep_score
                    best_move = move
                #Beta
                beta = min(beta, best_score)
                #Alpha
                if beta <= alpha:
                    break
        if track_move:
            return best_score, best_move
        return best_score
