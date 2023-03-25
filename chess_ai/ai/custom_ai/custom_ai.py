
import random
import time

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
        self.random_chance = 0.2

    def _sort_move(self, move_tuple: tuple) -> int:
        return -move_tuple[0]

    def _order_move_list(self, board: ChessBoard, board_state: ChessBoardState, moves: list, env) -> list:
        move_list = []
        move: ChessMove
        for move in moves:

            #Add If taking a piece
            piece_taking: ChessPiece = board_state.piece_board[move.new_position[0] * board.files + move.new_position[1]]
            piece_taking_value = env.chess.score.get_piece_worth(piece_taking)

            #Add if new positions has better bias
            piece_moving: ChessPiece = board_state.piece_board[move.piece.position[0] * board.files + move.piece.position[1]]
            move_difference = env.chess.score.get_position_difference(piece_moving, move.piece.position, move.new_position, board, board_state)

            #Remove if new position can be taken by a pawn
            this_piece_worth = env.chess.score.get_piece_worth(piece_moving)
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
    
    def _order_move_list_simple(self, board_state: ChessBoardState, moves: list, env) -> list:
        move_list = []
        move: ChessMove
        for move in moves:
            piece_taking: ChessPiece = board_state.piece_board[move.new_position[0] * env.chess.board.files + move.new_position[1]]
            piece_taking_value = env.chess.score.get_piece_worth(piece_taking)
            move_list.append((piece_taking_value, move))
        move_list.sort(key=self._sort_move)
        return move_list
    
    def _calc_attacks(self, env, board: ChessBoard, board_state: ChessBoardState, attacks: list, maximizePlayer: bool, alpha: int, beta: int, prune: bool):

        #Check each attack for their best move.
        best_score = -BIG_NUMBER if maximizePlayer else BIG_NUMBER
        new_alpha, new_beta = alpha, beta
        branches: int = 0
        sorted_list = self._order_move_list_simple(board_state, attacks, env)
        for _, move in sorted_list:
            new_board_state = board.move_piece(move, board_state, True)
            current_score = env.chess.score.calc_score(board, new_board_state)

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
                env, 
                board: ChessBoard, 
                board_state: ChessBoardState, 
                depth: int, 
                maximizePlayer: bool,
                prune: bool = True, 
                alpha: int = -BIG_NUMBER, 
                beta: int = BIG_NUMBER
    ):
        """Find the best move using minimax with Alpha-Beta Pruning.

        Args:
            maximizePlayer (bool): True if wanting to maximize score (White), False if wanting to minimize score (Black).
            alpha (int, optional): Previous Max Number (WHITE). Defaults to -BIG_NUMBER.
            beta (int, optional): Previous Min Number (BLACK). Defaults to BIG_NUMBER.
        """
        
        #Get Variables
        best_score = -BIG_NUMBER if maximizePlayer else BIG_NUMBER
        new_alpha, new_beta = alpha, beta
        best_move_list: list = [None]
        deep_move_list = [None]
        deep_move_list_temp = [None]
        branches: int = 0

        move_list = board_state.white_moves if maximizePlayer else board_state.black_moves
        sorted_list = self._order_move_list(board, board_state, move_list, env)
        
        #If depth == 0, return score of game
        for _, move in sorted_list:
            start = time.time() if depth == self.max_depth else 0

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
                        current_score, current_branches = self._calc_attacks(env, board, new_board_state, attacks, False, new_alpha, new_beta, prune)
                    else:
                        current_score = env.chess.score.calc_score(board, new_board_state)
                else:
                    current_score, deep_move_list_temp, current_branches = self.minimax(env, board, new_board_state, depth - 1, False, prune, new_alpha, new_beta)
                current_branches += 1

                #Prune if other player got a good score
                if current_score > new_beta and prune:
                    return current_score, best_move_list + deep_move_list_temp, branches + current_branches
                
                #Maximize
                if current_score > best_score:
                    best_score = current_score
                    best_move_list[0] = move
                    deep_move_list = deep_move_list_temp
                elif current_score == best_score and random.random() < self.random_chance:
                    best_score = current_score
                    best_move_list[0] = move
                    deep_move_list = deep_move_list_temp
                new_alpha = max(new_alpha, best_score)

            else:
                #Recurse to a depth of 0
                if depth == 0:
                    attacks = []
                    for r, f in new_board_state.white_positions:
                        piece: ChessPiece = new_board_state.piece_board[r * board.ranks + f]
                        attacks += piece.attacks
                    if len(attacks) != 0:
                        current_score, current_branches = self._calc_attacks(env, board, new_board_state, attacks, True, new_alpha, new_beta, prune)
                    else:
                        current_score = env.chess.score.calc_score(board, new_board_state)
                else:
                    current_score, deep_move_list_temp, current_branches = self.minimax(env, board, new_board_state, depth - 1, True, prune, new_alpha, new_beta)
                current_branches += 1

                #Prune if other player got a good score
                if current_score < new_alpha and prune:
                    return current_score, best_move_list + deep_move_list_temp, branches + current_branches

                #Minimize
                if current_score < best_score:
                    best_score = current_score
                    best_move_list[0] = move
                    deep_move_list = deep_move_list_temp
                elif current_score == best_score and random.random() < self.random_chance:
                    best_score = current_score
                    best_move_list[0] = move
                    deep_move_list = deep_move_list_temp
                new_beta = min(new_beta, best_score)

            branches += current_branches
            current_move_list = [move] + deep_move_list

            if depth == self.max_depth:
                end = time.time()
                e = round((end - start) * 1000, 3)
                if e > 1000:
                    move_str = ""
                    for move in current_move_list:
                        if move is not None:
                            move_str = move_str + " " + env.chess._calc_move_str(move, None, None)
                        else:
                            move_str = move_str + " NONE"
                    print(f"Depth: {depth}, Best Score: {best_score}, Total Branches: {branches} Current Branches: {current_branches}, Current Score: {current_score} (Move: {move_str}) Time Elapsed: {e} ms Alpha: {new_alpha}, Beta: {new_beta}")

        #Return new Data
        return best_score, best_move_list + deep_move_list, branches
        
    def execute_turn(self, board: ChessBoard, env):
        print(f"Calculating next move...")
        best_move: ChessMove
        start = time.time()
        best_score, best_move_list, branches = self.minimax(env, board, board.state, self.max_depth, True if env.chess.board.state.whites_turn else False, True)
        end = time.time()
        e = round((end-start) * 1000, 3)
        if best_move_list[0] is not None:
            move_str = ""
            for move in best_move_list:
                if move is not None:
                    move_str = move_str + " " + env.chess._calc_move_str(move, None, None)
                else:
                    move_str = move_str + " NONE"
            print(f"DONE! Branches Checked: {branches} and found Best Move: {move_str} with best score: {best_score} in {e} ms")
            env.chess.move_piece(best_move_list[0], env)