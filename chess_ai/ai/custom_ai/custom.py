
import random
import time
from multiprocessing.pool import Pool
from multiprocessing import cpu_count
from functools import partial

from ..base_ai import BaseAI
from ...chess_logic.chess_move import ChessMove
from ...chess_logic.chess_piece import ChessPiece
from ...chess_logic.chess_board import ChessBoardState, ChessBoard

#from ...environment import Environment

BIG_NUMBER = 10000000

class CustomAI(BaseAI):
    def __init__(self, is_white: bool, max_depth: int = 2, *args, **kwargs) -> None:
        super().__init__(is_white, *args, **kwargs)
        self.max_depth = max_depth
        self.mp_start_depth = 10
        self.random_chance = 0.2

    def _sort_move(self, move_tuple: tuple) -> int:
        return -move_tuple[0]

    def _order_move_list(self, board: ChessBoard, board_state: ChessBoardState, moves: list, score_class) -> list:
        move_list = []
        move: ChessMove
        for move in moves:

            #Add If taking a piece
            piece_taking: ChessPiece = board_state.piece_board[move.new_position[0] * board.files + move.new_position[1]]
            piece_taking_value = score_class.get_piece_worth(piece_taking)

            #Add if new positions has better bias
            piece_moving: ChessPiece = board_state.piece_board[move.piece.position[0] * board.files + move.piece.position[1]]
            move_difference = score_class.get_position_difference(piece_moving, move.piece.position, move.new_position, board, board_state)

            #Remove if new position can be taken by a pawn
            this_piece_worth = score_class.get_piece_worth(piece_moving)
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
    
    def _order_move_list_simple(self, board, board_state: ChessBoardState, moves: list, score_class) -> list:
        move_list = []
        move: ChessMove
        for move in moves:
            piece_taking: ChessPiece = board_state.piece_board[move.new_position[0] * board.files + move.new_position[1]]
            piece_taking_value = score_class.get_piece_worth(piece_taking)
            move_list.append((piece_taking_value, move))
        move_list.sort(key=self._sort_move)
        return move_list
    
    def _calc_attacks(self, score_class, board: ChessBoard, board_state: ChessBoardState, attacks: list, maximizePlayer: bool, alpha: int, beta: int, prune: bool):

        #Check each attack for their best move.
        best_score = -BIG_NUMBER if maximizePlayer else BIG_NUMBER
        new_alpha, new_beta = alpha, beta
        branches: int = 0
        sorted_list = self._order_move_list_simple(board, board_state, attacks, score_class)
        for _, move in sorted_list:
            new_board_state = board.move_piece(move, board_state, True)
            current_score = score_class.calc_score(board, new_board_state)

            #Maximize
            if maximizePlayer:
                #Prune if other player got a good score
                if current_score > new_beta and prune:
                    return current_score, branches
                #Maximize
                if current_score > best_score:
                    best_score = current_score
                elif current_score == best_score and random.random() < self.random_chance:
                    best_score = current_score
                new_alpha = max(new_alpha, best_score)
            #Minimize
            else:
                #Prune if other player got a good score
                if current_score < new_alpha and prune:
                    return current_score, branches
                #Minimize
                if current_score < best_score:
                    best_score = current_score
                elif current_score == best_score and random.random() < self.random_chance:
                    best_score = current_score
                new_beta = min(new_beta, best_score)
            branches += 1
        return best_score, branches
    
    def minimax(self, 
                score_class, 
                board: ChessBoard, 
                board_state: ChessBoardState, 
                depth: int, 
                maximizePlayer: bool,
                prune: bool = True, 
                alpha: int = -BIG_NUMBER, 
                beta: int = BIG_NUMBER,
    ) -> tuple[int, ChessMove, int]:
        """Find the best move using minimax with Alpha-Beta Pruning.

        Args:
            maximizePlayer (bool): True if wanting to maximize score (White), False if wanting to minimize score (Black).
            alpha (int, optional): Previous Max Number (WHITE). Defaults to -BIG_NUMBER.
            beta (int, optional): Previous Min Number (BLACK). Defaults to BIG_NUMBER.
        """
        
        #Get Variables
        best_score = -BIG_NUMBER if maximizePlayer else BIG_NUMBER
        new_alpha, new_beta = alpha, beta
        best_move: ChessMove = None
        branches: int = 0

        move_list = board_state.white_moves if maximizePlayer else board_state.black_moves
        sorted_list = self._order_move_list(board, board_state, move_list, score_class)
        
        #If depth == 0, return score of game
        for _, move in sorted_list:

            #Get new board with their move
            new_board_state = board.move_piece(move, board_state, True)
            current_branches = 0

            if maximizePlayer:
                #Recurse to a depth of 0
                if depth == 0:
                    attacks = []
                    for r, f in new_board_state.black_positions:
                        piece: ChessPiece = new_board_state.piece_board[r * board.ranks + f]
                        attacks += piece.attacks
                    if len(attacks) != 0:
                        current_score, current_branches = self._calc_attacks(score_class, board, new_board_state, attacks, False, new_alpha, new_beta, prune)
                    else:
                        current_score = score_class.calc_score(board, new_board_state)
                else:
                    current_score, _, current_branches = self.minimax(score_class, board, new_board_state, depth - 1, False, prune, new_alpha, new_beta)
                current_branches += 1

                #Prune if other player got a good score
                if current_score > new_beta and prune:
                    worst_score = BIG_NUMBER if maximizePlayer else -BIG_NUMBER
                    return worst_score, best_move, branches + current_branches
                
                #Maximize
                if current_score > best_score:
                    best_score = current_score
                    best_move = move
                elif current_score == best_score and random.random() < self.random_chance:
                    best_score = current_score
                    best_move = move
                new_alpha = max(new_alpha, best_score)

            else:
                #Recurse to a depth of 0
                if depth == 0:
                    attacks = []
                    for r, f in new_board_state.white_positions:
                        piece: ChessPiece = new_board_state.piece_board[r * board.ranks + f]
                        attacks += piece.attacks
                    if len(attacks) != 0:
                        current_score, current_branches = self._calc_attacks(score_class, board, new_board_state, attacks, True, new_alpha, new_beta, prune)
                    else:
                        current_score = score_class.calc_score(board, new_board_state)
                else:
                    current_score, _, current_branches = self.minimax(score_class, board, new_board_state, depth - 1, True, prune, new_alpha, new_beta)
                current_branches += 1

                #Prune if other player got a good score
                if current_score < new_alpha and prune:
                    worst_score = BIG_NUMBER if maximizePlayer else -BIG_NUMBER
                    return worst_score, best_move, branches + current_branches

                #Minimize
                if current_score < best_score:
                    best_score = current_score
                    best_move = move
                elif current_score == best_score and random.random() < self.random_chance:
                    best_score = current_score
                    best_move= move
                new_beta = min(new_beta, best_score)

            branches += current_branches

        #Return new Data
        return best_score, best_move, branches
    
    def minimax_mp_first(self, move: ChessMove, data: tuple[any, ChessBoard, ChessBoardState, int, bool, bool, int, int]) -> tuple[int, ChessMove, int]:
        #Unpack tuple
        score_class, board, board_state, depth, maximizePlayer, prune, alpha, beta = data

        #Get new board with their move
        new_board_state = board.move_piece(move, board_state, True)
        other_positions = new_board_state.black_positions if maximizePlayer else new_board_state.white_positions

        #Get Score Value of this Move
        if depth == 0:
            attacks = []
            current_score = 0
            for r, f in other_positions:
                piece: ChessPiece = new_board_state.piece_board[r * board.ranks + f]
                attacks += piece.attacks
            if len(attacks) != 0:
                current_score, current_branches = self._calc_attacks(score_class, board, new_board_state, attacks, not maximizePlayer, alpha, beta, prune)
            else:
                current_score = score_class.calc_score(board, new_board_state)
        else:
            current_score, _, current_branches = self.minimax(score_class, board, new_board_state, depth - 1, not maximizePlayer, prune, alpha, beta)

        #Return Data
        return current_score, move, current_branches + 1
    
    def minimax_mp(self, 
                score_class, 
                board: ChessBoard, 
                board_state: ChessBoardState, 
                depth: int, 
                maximizePlayer: bool,
                prune: bool = True, 
                alpha: int = -BIG_NUMBER, 
                beta: int = BIG_NUMBER,
    ):
        #Get Variables

        move_list = board_state.white_moves if maximizePlayer else board_state.black_moves
        if move_list is None:
            return 0, None, 0
        n_tasks = len(move_list)
        workers = cpu_count()-1
        chunk_size = int(n_tasks/workers)

        #If work is able to be done on more than one core
        if chunk_size >= 1:
            new_pool = Pool(int(workers))
            print(f"MP: {n_tasks} tasks. ")
            #Perform Multiprocessing on minimax
            part_func = partial(self.minimax_mp_first, data=(score_class, board, board_state, depth, maximizePlayer, prune, alpha, beta))
            results_async = [ new_pool.map_async(part_func, move_list, chunksize=chunk_size) ]
            results = [ pool.get() for pool in results_async]

            #Get the best result from the multiprocessing
            best_score = -BIG_NUMBER if maximizePlayer else BIG_NUMBER
            best_move: ChessMove = None
            branches: int = 0
            for result in results[0]:
                if result is not None:
                    current_score, current_move, current_branches = result
                    branches += current_branches

                    #Maximize or minimize player
                    if maximizePlayer:
                        if current_score > best_score:
                            best_score = current_score
                            best_move = current_move
                    else:
                        if current_score < best_score:
                            best_score = current_score
                            best_move = current_move
            #Return Best
            new_pool.close()
            return best_score, best_move, branches
        else:
            print(f"NO MP: {n_tasks} tasks.")
            #Return best from entire list
            return self.minimax(score_class, board, board_state, depth, maximizePlayer, prune, alpha, beta)
        
    def get_move(self, board: ChessBoard, env = None) -> ChessMove:
        print(f"Calculating next move...")
        best_move: ChessMove
        best_score, best_move, branches = None, None, 0
        score_class = env.chess.score
        if self.mp_start_depth <= self.max_depth:
            best_score, best_move, branches = self.minimax_mp(score_class, board, board.state, self.max_depth, True if env.chess.board.state.whites_turn else False, True)
        else:
            best_score, best_move, branches = self.minimax(score_class, board, board.state, self.max_depth, True if env.chess.board.state.whites_turn else False, True)
        print(f"DONE! Branches Checked: {branches}. with best score: {best_score}")
        return best_move
        
    def execute_turn(self, board: ChessBoard, env = None):
        print(f"Calculating next move...")
        if env is None:
            print("WARNING: Custom AI needs env.")
            return
        best_move: ChessMove
        start = time.time()
        best_score, best_move, branches = None, None, 0
        score_class = env.chess.score
        if self.mp_start_depth <= self.max_depth:
            best_score, best_move, branches = self.minimax_mp(score_class, board, board.state, self.max_depth, True if env.chess.board.state.whites_turn else False, True)
        else:
            best_score, best_move, branches = self.minimax(score_class, board, board.state, self.max_depth, True if env.chess.board.state.whites_turn else False, True)
        end = time.time()
        e = round((end-start) * 1000, 3)
        if best_move is not None:
            old_piece = env.chess.board.state.piece_board[best_move.new_position[0] * env.chess.board.files + best_move.new_position[1]]
            print(f"DONE! Branches Checked: {branches} and found Best Move: {env.chess._calc_move_str(best_move, old_piece, None)} with best score: {best_score} in {e} ms")
            env.chess.move_piece(best_move, env)