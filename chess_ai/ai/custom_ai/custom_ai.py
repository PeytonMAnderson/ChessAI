
import random

from ..base_ai import BaseAI

class CustomAI(BaseAI):
    def __init__(self, is_white: bool, max_depth: int = 2, *args, **kwargs) -> None:
        super().__init__(is_white, *args, **kwargs)
        self.max_depth = max_depth
        self.score_falloff_ratio = 0.90
        self.random_chance = 0.1

    def calc_their_best_move(self, 
                            board: list, 
                            is_white: bool, 
                            env, 
                            worst_prev_best_color_score: int, 
                            prune: bool = False, 
                            depth: int = 0
        ) -> tuple:
        #Get Variables
        best_score = None
        best_color_score = None
        best_move = None
        branches = 0

        #Loop through their moves to see what they would choose
        moves_list = env.chess.moves.get_all_valid_moves(board, env.chess.state.castle_avail, env.chess.state.en_passant, is_white)
        for ro, fo, rf, ff in moves_list:
            #Get their new board for their moves
            new_board = env.chess.base_moves.base_move(ro, fo, rf, ff, board)
            new_score = env.chess.score.calc_game_score(new_board, not is_white)

            #Recurse if their is a recurse function
            deep_score, _, deep_branches = 0, None, 0
            if depth > 0:
                deep_score, _, deep_branches = self.calc_best_recursion(new_board, env, not is_white, depth - 1)
            branches += deep_branches

            #Calculate their score
            total_score = new_score + deep_score * self.score_falloff_ratio
            total_color_score = total_score if is_white else 0 - total_score

            #If their new score is their best one yet, save their values
            if best_color_score is None or total_color_score > best_color_score:
                best_color_score = total_color_score
                best_score = total_score
                best_move = (ro, fo, rf, ff)

            branches += 1

            #Prune branch if found value higher than previous
            if worst_prev_best_color_score is not None and prune:
                if total_color_score > worst_prev_best_color_score:
                    return best_score, best_move, branches
        return best_score, best_move, branches
    
    def calc_our_best_move(self, board: list, env, is_white: bool, depth: int = 0) -> tuple:
        #Get Variables
        best_score = None
        best_color_score = None
        best_move = None
        branches = 0
        worst_prev_best_color_score = None

        #Loop through all of our moves to see the best option
        moves_list = env.chess.moves.get_all_valid_moves(board, env.chess.state.castle_avail, env.chess.state.en_passant, is_white)
        for ro, fo, rf, ff in moves_list:
            #Get new boards with our moves
            new_board = env.chess.base_moves.base_move(ro, fo, rf, ff, board)
            new_score = env.chess.score.calc_game_score(new_board, not is_white)

            #Calculate what their best response would be
            their_best_score, _, their_branches = None, None, 0
            if depth > 0:
                their_best_score, _, their_branches = self.calc_their_best_move(new_board, not is_white, env, worst_prev_best_color_score, True, depth - 1)
            branches += their_branches

            #Calculate new total score from our score and their best score
            total_score = new_score
            if their_best_score is not None:
                their_best_color_score = their_best_score if not is_white else 0 - their_best_score
                worst_prev_best_color_score = their_best_color_score if worst_prev_best_color_score is None or their_best_color_score < worst_prev_best_color_score else worst_prev_best_color_score
                total_score + their_best_score
            total_color_score = total_score if is_white else 0 - total_score

            #If the new total score is the best one yet, store values
            if best_color_score is None or total_color_score > best_color_score:
                best_color_score = total_color_score
                best_score = total_score
                best_move = (ro, fo, rf, ff)

            branches += 1
        return best_score, best_move, branches
    
    def calc_best_recursion(self, board: list, env, is_white: bool, depth: int = 0):
        best_move = self.calc_our_best_move(board, env, is_white, depth)
        print(f"Depth: {depth}  Best Move: {best_move}")
        return best_move
        
    def execute_turn(self, board: list, env):
        print("EXECUTE")
        best_score, best_move, branches = self.calc_best_recursion(board, env, self.is_white, self.max_depth)
        print(f"DONE! Branches Checked: {branches} and found Best Move: {best_move} with best score: {best_score}")
        if best_move is not None:
            ro, fo, rf, ff = best_move
            env.chess.move_piece(ro, fo, rf, ff)
        return 

    # def calc_best_move_recurse(self, board: list, depth: int, env, is_white: bool) -> tuple | None:
    #     best_score = None
    #     best_move = None
    #     branches = 0
    #     if depth == 0:
    #         moves_list = env.chess.moves.get_all_valid_moves(board, env.chess.state.castle_avail, env.chess.state.en_passant, is_white)
    #         their_bestest_score = None
    #         for our_ro, our_fo, our_rf, our_ff in moves_list:
    #             our_board = env.chess.base_moves.base_move(our_ro, our_fo, our_rf, our_ff, board)
    #             our_score = env.chess.score.calc_game_score(board, is_white)
    #             their_best_move = self.calc_best_move(our_board, not is_white, env)
    #             if their_best_move is not None:
    #                 branches += their_best_move[2]
    #                 their_color_score = their_best_move[0] if not is_white else 0 - their_best_move[0]
    #                 their_bestest_score = their_color_score if their_bestest_score is None or their_color_score > their_bestest_score else their_bestest_score
    #             total_score = our_score + their_best_move[0] if their_best_move is not None else our_score
    #             color_score = total_score if is_white else 0 - total_score
    #             if best_score is None or color_score > best_score:
    #                 best_score = color_score
    #                 best_move = (our_ro, our_fo, our_rf, our_ff)
    #             elif color_score == best_score and random.random() < self.random_chance:
    #                 best_score = color_score
    #                 best_move = (our_ro, our_fo, our_rf, our_ff)
    #     else:
    #         new_depth = depth - 1
    #         their_worst_score = None
    #         moves_list = env.chess.moves.get_all_valid_moves(board, env.chess.state.castle_avail, env.chess.state.en_passant, is_white)
    #         for our_ro, our_fo, our_rf, our_ff in moves_list:
    #             our_board = env.chess.base_moves.base_move(our_ro, our_fo, our_rf, our_ff, board)
    #             our_score = env.chess.score.calc_game_score(board, is_white)
    #             new_their_best_score, new_their_best_move, new_their_branches = self.calc_best_move(our_board, not is_white, env)
    #             branches += new_their_branches + 1
    #             if new_their_best_score is not None: 
    #                 their_score_adj = new_their_best_score if not is_white else 0 - new_their_best_score
    #                 if their_worst_score is None or their_score_adj < their_worst_score:
    #                     their_worst_score = their_score_adj
    #                     total_score = our_score + new_their_best_score if new_their_best_score is not None else our_score
    #                     t_ro, t_fo, t_rf, t_ff = new_their_best_move
    #                     their_board = env.chess.base_moves.base_move(t_ro, t_fo, t_rf, t_ff, our_board)
    #                     deep_best_score, _, deep_branches = self.calc_best_move_recurse(their_board, new_depth, env, is_white)
    #                     total_score_deep = total_score + deep_best_score * self.score_falloff_ratio if deep_best_score is not None else total_score
    #                     print(f"Depth: {depth}, Best: {best_score}: Score: {total_score_deep} Their worse: {their_worst_score}")
    #                     if best_score is None or total_score_deep > best_score:
    #                         best_score = total_score_deep
    #                         best_move = (our_ro, our_fo, our_rf, our_ff)
    #                     elif total_score_deep == best_score and random.random() < self.random_chance:
    #                         best_score = total_score_deep
    #                         best_move = (our_ro, our_fo, our_rf, our_ff)
    #                     branches += deep_branches
    #     return best_score, best_move, branches


