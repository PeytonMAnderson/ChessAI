
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

    def _order_move_list(self, board_state: ChessBoardState, moves: list, env) -> list:
        move_list = []
        move: ChessMove
        for move in moves:
            piece: ChessPiece = board_state.piece_board[move.new_position[0] * env.chess.board.files + 1]
            piece_score = env.chess.score.get_piece_score_king(piece)
            move_list.append((piece_score, move))
        move_list.sort(key=self._sort_move)
        return move_list
    
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
        sorted_list = self._order_move_list(board_state, move_list, env)
        
        #If depth == 0, return score of game
        for _, move in sorted_list:
            start = time.time() if depth == self.max_depth else 0

            #Get new board with their move
            new_board_state = board.move_piece(move, board_state, True)
            current_branches = 0

            if maximizePlayer:
                #Recurse to a depth of 0
                if depth == 0:
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