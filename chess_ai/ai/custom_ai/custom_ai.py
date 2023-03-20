
import random

from ..base_ai import BaseAI

class CustomAI(BaseAI):
    def __init__(self, is_white: bool, max_depth: int = 2, *args, **kwargs) -> None:
        super().__init__(is_white, *args, **kwargs)
        self.max_depth = max_depth
        self.score_falloff_ratio = 0.90
        self.random_chance = 0.1

    def calc_best_move(self, board: list, is_white: bool, env) -> tuple | None:
        best_score = None
        best_color_score = None
        best_move = None
        branches = 0
        moves_list = env.chess.moves.get_all_valid_moves(board, env.chess.state.castle_avail, env.chess.state.en_passant, is_white)
        for ro, fo, rf, ff in moves_list:
            new_board = env.chess.base_moves.base_move(ro, fo, rf, ff, board)
            new_score = env.chess.score.calc_game_score(new_board, is_white)
            color_score = new_score if is_white else 0 - new_score
            if best_color_score is None or color_score > best_color_score:
                best_color_score = color_score
                best_score = new_score
                best_move = (ro, fo, rf, ff)
            branches += 1
        return best_score, best_move, branches

    def calc_best_move_recurse(self, board: list, depth: int, env, is_white: bool) -> tuple | None:
        best_score = None
        best_move = None
        branches = 0
        if depth == 0:
            moves_list = env.chess.moves.get_all_valid_moves(board, env.chess.state.castle_avail, env.chess.state.en_passant, is_white)
            for our_ro, our_fo, our_rf, our_ff in moves_list:
                our_board = env.chess.base_moves.base_move(our_ro, our_fo, our_rf, our_ff, board)
                our_score = env.chess.score.calc_game_score(board, is_white)
                their_best_score, _, their_branches = self.calc_best_move(our_board, not is_white, env)
                total_score = our_score + their_best_score if their_best_score is not None else our_score
                branches += their_branches
                color_score = total_score if is_white else 0 - total_score
                print(f"Best: {best_score}: Score: {color_score} ({total_score})")
                if best_score is None or color_score > best_score:
                    best_score = color_score
                    best_move = (our_ro, our_fo, our_rf, our_ff)
                elif color_score == best_score and random.random() < self.random_chance:
                    best_score = color_score
                    best_move = (our_ro, our_fo, our_rf, our_ff)
        else:
            new_depth = depth - 1
            moves_list = env.chess.moves.get_all_valid_moves(board, env.chess.state.castle_avail, env.chess.state.en_passant, is_white)
            for our_ro, our_fo, our_rf, our_ff in moves_list:
                our_board = env.chess.base_moves.base_move(our_ro, our_fo, our_rf, our_ff, board)
                their_moves_list = env.chess.moves.get_all_valid_moves(our_board, env.chess.state.castle_avail, env.chess.state.en_passant, not is_white)
                for their_ro, their_fo, their_rf, their_ff in their_moves_list:
                    their_board = env.chess.base_moves.base_move(their_ro, their_fo, their_rf, their_ff, our_board)
                    new_score = env.chess.score.calc_game_score(their_board, is_white)
                    color_score = new_score if is_white else 0 - new_score
                    best_deep_score, _, deep_branches = self.calc_best_move_recurse(their_board, new_depth, env, is_white)
                    adj_score = color_score + best_deep_score * self.score_falloff_ratio
                    if best_score == None or adj_score > best_score:
                        best_score = adj_score
                        best_move = (our_ro, our_fo, our_rf, our_ff)
                    elif color_score == best_score and random.random() < self.random_chance:
                        best_score = color_score
                        best_move = (our_ro, our_fo, our_rf, our_ff)
                    branches += deep_branches
        return best_score, best_move, branches

    def execute_turn(self, board: list, env):
        print("EXECUTE")
        best_score, best_move, branches = self.calc_best_move_recurse(board, self.max_depth, env, self.is_white)
        print(f"DONE! Branches Checked: {branches} and found Best Move: {best_move} with best score: {best_score}")
        if best_move is not None:
            ro, fo, rf, ff = best_move
            env.chess.move_piece(ro, fo, rf, ff)
        return 
