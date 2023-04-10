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

    def _prune_score_function(self, best_score: float, maxmimize: bool, alpha: float = None, beta: float = None) -> tuple[float, float, bool]:
        if alpha is None or beta is None:
            return (None, None, False)
        new_alpha = max(alpha, best_score) if maxmimize else alpha
        new_beta = min(beta, best_score) if not maxmimize else beta
        if beta <= alpha:
            return (new_alpha, new_beta, True)
        return (new_alpha, new_beta, False)

    def _get_best_score(self, best_score: float, best_move: ChessMove, new_score: float, new_move: ChessMove, maximize: bool) -> tuple[float, ChessMove]:
        update = True if (maximize and new_score > best_score) or (not maximize and new_score < best_score) else False
        return (new_score, new_move) if update else (best_score, best_move)

    def _best_score_function(self, board: ChessBoard, board_state: ChessBoardState, sorted: bool = True, alpha: float = None, beta: float = None) -> tuple[float, ChessMove]:
        move_list = board_state.white_moves if board_state.whites_turn else board_state.black_moves
        sorted_list = move_list if not sorted else self._order_move_list(board, board_state, move_list)
        best_score = -BIG_NUMBER if board_state.whites_turn else BIG_NUMBER
        best_move = None
        branches = 0
        new_alpha = alpha
        new_beta = beta
        move: ChessMove
        for move in sorted_list:
            branches += 1
            move = move[1] if isinstance(move, tuple) else move
            new_board_state = board.move_piece(move, board_state, True)
            new_score = self.score.calc_score(board, new_board_state)
            best_score, best_move = self._get_best_score(best_score, best_move, new_score, move, board_state.whites_turn)
            new_alpha, new_beta, prune = self._prune_score_function(best_score, board_state.whites_turn, new_alpha, new_beta)
            if prune:
                break
        if len(sorted_list) == 0:
            return self.score.calc_score(board, board_state), best_move, branches   
        return best_score, best_move, branches   

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
            score, move, branches = self.calc_best_score(board, board_state, True, alpha, beta)
            if track_move:
                return score, move, branches
            return score, branches
        
        #Depth > 0: Recurse to depth == 0
        best_score = -BIG_NUMBER if board_state.whites_turn else BIG_NUMBER
        best_move = None
        branches = 0
        new_alpha = alpha
        new_beta = beta

        #Sort Moves
        move_list = board_state.white_moves if board_state.whites_turn else board_state.black_moves
        sorted_list = move_list if not sorted else self._order_move_list(board, board_state, move_list)
        move: ChessPiece
        for move in sorted_list:
            move = move[1] if isinstance(move, tuple) else move
            new_board_state = board.move_piece(move, board_state, True)
            deep_score, deep_branches = self.minimax(board, new_board_state, new_alpha, new_beta, depth - 1, sorted, False)
            best_score, best_move = self._get_best_score(best_score, best_move, deep_score, move, board_state.whites_turn)
            new_alpha, new_beta, prune = self._prune_score_function(best_score, board_state.whites_turn, new_alpha, new_beta)
            if prune:
                break
            branches += deep_branches
            
        if track_move:
            return best_score, best_move, branches
        return best_score, branches
