
import random


from ..base_ai import BaseAI
from ...chess_logic.chess_move import ChessMove
from ...chess_logic.chess_piece import ChessPiece
from ...chess_logic.chess_board import ChessBoard
#from ...environment import Environment

class CustomAI(BaseAI):
    def __init__(self, is_white: bool, max_depth: int = 2, *args, **kwargs) -> None:
        super().__init__(is_white, *args, **kwargs)
        self.max_depth = max_depth
        self.score_falloff_ratio = 0.90
        self.random_chance = 0.1

    def _sort_move(self, move_tuple: tuple) -> int:
        return -move_tuple[0]

    def _order_move_list(self, moves: list, env) -> list:
        move_list = []
        move: ChessMove
        for move in moves:
            piece: ChessPiece = env.chess.board.piece_board[move.new_position[0] * env.chess.board.files + 1]
            piece_score = env.chess.score.get_piece_score_king(piece)
            move_list.append((piece_score, move))
        move_list.sort(key=self._sort_move)
        return move_list

    def calc_their_best_move(self, 
                            board: ChessBoard, 
                            env, 
                            worst_prev_best_color_score: int, 
                            prune: bool = False, 
                            depth: int = 0
        ) -> tuple:

        #Get Variables
        best_score: int = None
        best_color_score: int = None
        best_move: ChessMove = None
        branches: int = 0

        #Loop through their moves to see what they would choose
        move_list = board.white_moves if board.whites_turn else board.black_moves
        sorted_list = self._order_move_list(move_list, env)
        move: ChessMove
        for _, move in sorted_list:
            #Get new board with their move
            new_board = board.move_piece(move, True)
            new_score = env.chess.score.calc_score(new_board)

            #Prune branch if found value higher than previous
            if worst_prev_best_color_score is not None and prune:
                new_color_score = new_score if board.whites_turn else -new_score
                if new_color_score > worst_prev_best_color_score:
                    #print(f"\t\tPRUNED:\t\tOur Best: {best_color_score}, Current Score: {new_color_score} Current Move: {env.chess._calc_move_str(move, board, new_board.check_status)}")
                    return best_score, best_move, branches, True
                
            #Recurse if their is a recurse function
            deep_score, _, deep_branches = 0, None, 0
            if depth > 0:
                deep_score, _, deep_branches = self.calc_best_recursion(
                    new_board, 
                    env, 
                    depth - 1
                )
            branches += deep_branches

            #Calculate their score
            total_score = new_score + deep_score * self.score_falloff_ratio if deep_score is not None else new_score
            total_color_score = total_score if board.whites_turn else -total_score

            #print(f"\t\tOur Best: {best_color_score}, Current Score: {total_color_score} Current Move: {env.chess._calc_move_str(move, board, new_board.check_status)}")

            #If their new score is their best one yet, save their values
            if best_color_score is None or total_color_score > best_color_score:
                best_color_score = total_color_score
                best_score = total_score
                best_move = move
            elif total_color_score == best_color_score and random.random() < self.random_chance:
                best_color_score = total_color_score
                best_score = total_score
                best_move = move
            branches += 1

        return best_score, best_move, branches, False
    
    def calc_our_best_move(self, board: ChessBoard, env, depth: int = 0) -> tuple:
        #Get Variables
        best_score: int = None
        best_color_score: int = None
        best_move: ChessMove = None
        branches: int = 0

        #Loop through all of our moves to see the best option
        move_list = board.white_moves if board.whites_turn else board.black_moves
        sorted_list = self._order_move_list(move_list, env)
        move: ChessMove
        worst_prev_best_color_score = None
        for _, move in sorted_list:

            #Get new board with our move
            new_board = board.move_piece(move, True)
            new_score = env.chess.score.calc_score(new_board)

            #Calculate what their best response would be
            their_best_score, _, their_branches, pruned = None, None, 0, False
            if depth > 0:
                their_best_score, _, their_branches, pruned = self.calc_their_best_move(
                    new_board, 
                    env, 
                    worst_prev_best_color_score,
                    True,
                    depth - 1
                )
            branches += their_branches
            if pruned:
                continue
            
            #Calculate new total score from our score and their best score
            #print(f"Their Worst: {worst_prev_best_color_score} Their Current: {their_best_score}, Our Best: {best_color_score}, Current Move: {env.chess._calc_move_str(move, board, new_board.check_status)}")
            total_score = new_score
            if their_best_score is not None:
                their_best_color_score = their_best_score if not board.whites_turn else 0 - their_best_score
                worst_prev_best_color_score = their_best_color_score if worst_prev_best_color_score is None or their_best_color_score < worst_prev_best_color_score else worst_prev_best_color_score
                
                total_score = total_score + their_best_score
            total_color_score = total_score if board.whites_turn else 0 - total_score

            #print(f"Best Move: {best_move}, Best Score: {best_score}, Total Score: {total_score}, Our Score: {new_score}, Their Best: {their_best_score}")

            #If the new total score is the best one yet, store values
            if best_color_score is None or total_color_score > best_color_score:
                best_color_score = total_color_score
                best_score = total_score
                best_move =  move
            elif total_color_score == best_color_score and random.random() < self.random_chance:
                best_color_score = total_color_score
                best_score = total_score
                best_move =  move
            branches += 1

        return best_score, best_move, branches
    
    def calc_best_recursion(self, board: ChessBoard, env, depth: int = 0):
        best_move = self.calc_our_best_move(board, env, depth)
        #print(f"Depth: {depth}  Best Move: {best_move}")
        return best_move
        
    def execute_turn(self, board: ChessBoard, env):
        print(f"Calculating next move...")
        best_move: ChessMove
        best_score, best_move, branches = self.calc_best_recursion(board, env, self.max_depth)
        if best_move is not None:
            print(f"DONE! Branches Checked: {branches} and found Best Move: {env.chess._calc_move_str(best_move, env.chess.board)} with best score: {best_score}")
            env.chess.move_piece(best_move, env)