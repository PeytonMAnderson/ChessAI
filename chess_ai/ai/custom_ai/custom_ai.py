
import random


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
        best_move: ChessMove = None
        branches: int = 0

        move_list = board_state.white_moves if maximizePlayer else board_state.black_moves
        sorted_list = self._order_move_list(board_state, move_list, env)
        
        #If depth == 0, return score of game
        for _, move in sorted_list:

            #Get new board with their move
            new_board_state = board.move_piece(move, True)
            current_branches = 0

            if maximizePlayer:
                #Recurse to a depth of 0
                if depth == 0:
                    current_score = env.chess.score.calc_score(board, new_board_state)
                else:
                    current_score, _, current_branches = self.minimax(env, board, new_board_state, depth - 1, False, alpha, beta)
                current_branches += 1
                
                #Maximize
                if current_score > best_score:
                    best_score = current_score
                    best_move = move
                elif current_score == best_score and random.random() < self.random_chance:
                    best_score = current_score
                    best_move = move
                alpha = max(alpha, best_score)

            else:
                #Recurse to a depth of 0
                if depth == 0:
                    current_score = env.chess.score.calc_score(board, new_board_state)
                else:
                    current_score, _, current_branches = self.minimax(env, board, new_board_state, depth - 1, True, alpha, beta)
                current_branches += 1

                #Minimize
                if current_score < best_score:
                    best_score = current_score
                    best_move = move
                elif current_score == best_score and random.random() < self.random_chance:
                    best_score = current_score
                    best_move = move
                beta = min(beta, best_score)

            branches += current_branches

        #Return new Data
        return best_score, best_move, branches
        
    def execute_turn(self, board: ChessBoard, env):
        print(f"Calculating next move...")
        best_move: ChessMove
        best_score, best_move, branches = self.minimax(env, board, board.state, self.max_depth, True if env.chess.board.state.whites_turn else False)
        if best_move is not None:
            print(f"DONE! Branches Checked: {branches} and found Best Move: {env.chess._calc_move_str(best_move, env.chess.board)} with best score: {best_score}")
            env.chess.move_piece(best_move, env)