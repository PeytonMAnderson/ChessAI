"""

    Global Variable Class for tracking Chess Variables

"""
import yaml
import time
import random
from copy import deepcopy

from .chess_move import ChessMove
from .chess_piece import ChessPiece
from .chess_utils import ChessUtils
from .chess_board import ChessBoard, ChessBoardState    
from .chess_history import ChessHistory
from .chess_score import ChessScore

BIG_NUMBER = 10000000

#Global Variable Class
class GlobalChess:
    def __init__(self,
                 board_files: int = 8,
                 board_ranks: int = 8,
                 max_half_moves: int = 50,
                 piece_values: dict = {},
                 piece_scores: dict = {},
                 starting_fen: str = "",
    *args, **kwargs) -> None:
        
        #Attach Chess Objects
        self.board = ChessBoard(ChessUtils(piece_values), board_ranks, board_files)
        self.score = ChessScore(piece_scores)
        self.history = ChessHistory()
        self.check_status_str = "None"
        self.last_move_str = "None"
        self.last_move_tuple = None
        self.game_ended = False
        self.max_half_moves = max_half_moves
        self.tree = []
        self.max_depth = 0
        self.random_chance = 0.2
        self.starting_fen = starting_fen
    
    def _calc_check_status_str(self) -> "GlobalChess":
        """Calculates and sets the check_status_str from check_status.

        Args:
            board (ChessBoard): The board that contains the check_status

        Returns:
            GlobalChess: Self for chaining.
        """
        if self.board.state.check_status is None:
            self.check_status_str = "None"
        elif self.board.state.check_status == 2:
            self.check_status_str = "White Checkmate"
        elif self.board.state.check_status == 1:
            self.check_status_str = "White Check"
        elif self.board.state.check_status == 0:
            self.check_status_str = "Stalemate"
        elif self.board.state.check_status == -1:
            self.check_status_str = "Black Check"
        elif self.board.state.check_status == -2:
            self.check_status_str = "Black Checkmate"
        return self
    
    def _calc_move_str(self, old_move: ChessMove, old_piece: ChessPiece | None, new_check_status: int = None) -> str:
        """Generates a Move string such as (e4, Rxf7, Qf1+, etc.)

        Args:
            move (ChessMove): The move that is about to be taken.
            board (ChessBoard): The board before the move to determine if a capture occured.

        Returns:
            str: A Move string detailing the move that will be taken.
        """
        #Get rank and file str
        rank = self.board.utils.get_rank_from_number(old_move.new_position[0], self.board.ranks)
        file = self.board.utils.get_file_from_number(old_move.new_position[1])

        #Get Castle String
        if old_move.castle:
            if old_move.new_position[1] - old_move.piece.position[1] > 0:
                return "O-O"
            else:
                return "O-O-O"

        #Get check string
        check_str = ""
        if new_check_status is not None:
            if abs(new_check_status) == 2:
                check_str = "#"
            elif abs(new_check_status) == 1: 
                check_str = "+"
        
        #Get piece str
        piece_str = ""
        if old_move.piece.type != "P":
            piece_str = old_move.piece.type
        else:
            prev_file = self.board.utils.get_file_from_number(old_move.piece.position[1])
            if prev_file != file:
                piece_str = prev_file

        #Get Piece was captured
        captured_str = ""
        if old_piece is not None:
            captured_str = "x"
        return piece_str + captured_str + file + rank + check_str

    def move_piece(self, move: ChessMove, env = None) -> "GlobalChess":
        """Moves a piece on the board assuming the move if valid. Updates score, history, game_ended, and last move.

        Args:
            move (ChessMove): The move that will be taken place.

        Returns:
            GlobalChess: Self for chaining.
        """
        if self.game_ended is True:
            return

        #Move Piece
        old_piece = deepcopy(self.board.state.piece_board[move.new_position[0] * self.board.files + move.new_position[1]])
        old_move = deepcopy(move)
        self.last_move_tuple = (move.piece.position[0], move.piece.position[1], move.new_position[0], move.new_position[1])
        self.board.move_piece(move, self.board.state)
        self._calc_check_status_str()
        self.last_move_str = self._calc_move_str(old_move, old_piece, self.board.state.check_status)

        #Get score
        self.score.update_score(self.board, self.board.state)
        env.visual.shapes.update_score_bar(env)

    
        #Calc if game ended
        if self.board.state.check_status is not None and abs(self.board.state.check_status) == 2 or self.board.state.check_status == 0:
            self.game_ended = True
        elif self.board.state.half_move >= self.max_half_moves:
            self.game_ended = True
        else:
            self.game_ended = False
        fen = self.board.board_to_fen()
        print(fen)
        self.history.pop_add({"last_move_str": self.last_move_str, 
                              "last_move_tuple": self.last_move_tuple, 
                              "fen_string":fen})
        
        if env is not None:
            if self.last_move_str.count("x") > 0:
                env.sound.play("capture", env)
            else:
                env.sound.play("move-self", env)
        
        # moves = self.board.state.white_moves if self.board.state.whites_turn else self.board.state.black_moves
        # best_score, best_move_list, branches = self.minimax(env, self.board, self.board.state, self.max_depth, self.board.state.whites_turn, True, create_tree=True)
        # if best_move_list[0] is not None:
        #     move_str = ""
        #     for move in best_move_list:
        #         if move is not None:
        #             move_str = move_str + " " + env.chess._calc_move_str(move, None, None)
        #         else:
        #             move_str = move_str + " NONE"
        #     print(f"DONE! Branches Checked: {branches} and found Best Move: {move_str} with best score: {best_score}")
        # env.visual.shapes.generate_tree(env)


    def load_from_history(self, frame: dict, env) -> "GlobalChess":
        """Load a state of the game from history. Updates score, history, game_ended, and last move.

        Args:
            frame (dict): The frame data that will be used to update the state.
                        Includes:
                            "last_move_str"
                            "last_move_tuple"
                            "fen_string"

        Returns:
            GlobalChess: Self for chaining.
        """
        self.board.fen_to_board(frame['fen_string'])
        self.last_move_str = frame['last_move_str']
        self.last_move_tuple = frame['last_move_tuple']
        self.score.update_score(self.board, self.board.state)
        env.visual.shapes.update_score_bar(env)
        self._calc_check_status_str()

        #Calc if game ended
        if self.board.state.check_status is not None and abs(self.board.state.check_status) == 2 or self.board.state.check_status == 0:
            self.game_ended = True
        elif self.board.state.half_move >= self.max_half_moves:
            self.game_ended = True
        else:
            self.game_ended = False

    def set_from_yaml(self, yaml_path: str) -> "GlobalChess":
        """Set up chess from yaml config file.

        Args:
            yaml_path (str): Path to the config file.

        Returns:
            GlobalChess: Self for chaining.
        """
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            settings = yaml_settings['CHESS']

            #Save Board Chess Values
            self.board.files = settings['BOARD_FILES']
            self.board.ranks = settings['BOARD_RANKS']
            self.board.utils.piece_values = settings['PIECE_VALUES']
            self.score.piece_scores = settings['PIECE_SCORES']
            self.board.fen_to_board(settings['BOARD'])
            self.starting_fen = settings['BOARD']
            self.max_half_moves = settings['MAX_HALF_MOVES']
            self.score.max_half_moves = self.max_half_moves
            self.score.calc_position_bias(self.board)
            self.score.set_max_score(self.board, self.board.state)

            #Start history
            self.history.pop_add({"last_move_str": "None", "last_move_tuple": None, "fen_string": settings['BOARD']})
        return self
    
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
                beta: int = BIG_NUMBER,
                create_tree: bool = False
    ):
        """Find the best move using minimax with Alpha-Beta Pruning.

        Args:
            maximizePlayer (bool): True if wanting to maximize score (White), False if wanting to minimize score (Black).
            alpha (int, optional): Previous Max Number (WHITE). Defaults to -BIG_NUMBER.
            beta (int, optional): Previous Min Number (BLACK). Defaults to BIG_NUMBER.
        """
        
        #Get Variables
        if create_tree:
            self.tree = [] if depth == self.max_depth else self.tree
        current_tree = []
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
                    if create_tree:
                        current_tree.append((current_score, move, maximizePlayer))
                else:
                    current_score, deep_move_list_temp, current_branches, branch_tree = self.minimax(env, board, new_board_state, depth - 1, False, prune, new_alpha, new_beta, create_tree)
                    if create_tree:
                        current_tree.append(branch_tree)
                current_branches += 1

                #Prune if other player got a good score
                if current_score > new_beta and prune:
                    worst_score = BIG_NUMBER if maximizePlayer else -BIG_NUMBER
                    return worst_score, best_move_list + deep_move_list_temp, branches + current_branches, [(worst_score, best_move_list[0], maximizePlayer), current_tree]
                
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
                    if create_tree:
                        current_tree.append((current_score, move, maximizePlayer))
                else:
                    current_score, deep_move_list_temp, current_branches, branch_tree = self.minimax(env, board, new_board_state, depth - 1, True, prune, new_alpha, new_beta, create_tree)
                    if create_tree:
                        current_tree.append(branch_tree)
                current_branches += 1

                #Prune if other player got a good score
                if current_score < new_alpha and prune:
                    worst_score = BIG_NUMBER if maximizePlayer else -BIG_NUMBER
                    return worst_score, best_move_list + deep_move_list_temp, branches + current_branches, [(worst_score, best_move_list[0], maximizePlayer), current_tree]

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
        if depth == self.max_depth:
            if create_tree:
                self.tree = [(best_score, best_move_list[0], maximizePlayer), current_tree]
            return best_score, best_move_list + deep_move_list, branches
        else:
            return best_score, best_move_list + deep_move_list, branches, [(best_score, best_move_list[0], maximizePlayer), current_tree]