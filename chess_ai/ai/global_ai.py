import yaml

from .base_ai import BaseAI
from ..chess_logic import *

from .custom_ai.custom import CustomAI
from .stockfish.stock_ai import StockFishAI
from .random.random_ai import RandomAI
from .policy_network.policy_network import PolicyAI
from ..minimax import Minimax, MinimaxAlphaBeta

class GlobalAI:
    def __init__(self,
          custom_depth: int = 0,
          white_player_str: str = "PLAYER",
          black_player_str: str = "PLAYER",
          paused: bool = False,  
          minimax: Minimax = None,
    *args, **kwargs) -> None:
        self.minimax = minimax
        if minimax is None:
            self.minimax = MinimaxAlphaBeta(None)
        self.custom_depth = custom_depth
        self.white_player_str = white_player_str
        self.black_player_str = black_player_str
        self.white_player = None
        self.black_player = None
        self.paused = paused

    def get_player_from_str(self, player_str: str, score: ChessScore, flag = None) -> None:
        if player_str == "PLAYER":
            return None
        elif player_str == "CUSTOM":
            return CustomAI(score, self.minimax, self.custom_depth)
        elif player_str == "STOCKFISH":
            return StockFishAI(score, 0.1)
        elif player_str == "RANDOM":
            return RandomAI(score)
        elif player_str == "POLICY":
            if flag == 1:
                return PolicyAI(score, self.minimax, './chess_ai/ai/policy_network/models/policy_network.model', self.custom_depth)
            elif flag == 2:
                return PolicyAI(score, self.minimax, './chess_ai/ai/policy_network/models/policy_network2.model', self.custom_depth)

    def set_players(self, score: ChessScore):
        self.white_player = self.get_player_from_str(self.white_player_str, score, 1)
        self.black_player = self.get_player_from_str(self.black_player_str, score, 2)

    def execute_player(self, player_str: str, player_value: BaseAI | None, board: ChessBoard, env): 
        if player_str == "PLAYER":
            return
        else:
            player_value.execute_turn(board, env)

    def execute_turn(self, board: ChessBoard, env): 
        if env.chess.game_ended or self.paused:
            return
        if board.state.whites_turn:
            self.execute_player(self.white_player_str, self.white_player, board, env)
        else:
            self.execute_player(self.black_player_str, self.black_player, board, env)

    def _create_chess_score(self, yaml_dict: dict) -> ChessScore:
        #Save Board Chess Values
        settings = yaml_dict['CHESS']
        files = settings['BOARD_FILES']
        ranks = settings['BOARD_RANKS']
        piece_values = settings['PIECE_VALUES']
        starting_fen = settings['BOARD']
        board = ChessBoard(ChessUtils(piece_values), ranks, files)
        board.fen_to_board(starting_fen)

        #Getting ChessScore
        piece_scores = settings['PIECE_SCORES']
        max_half_moves = settings['MAX_HALF_MOVES']
        score = ChessScore(piece_scores, max_half_moves)
        score.calc_position_bias(board)
        score.set_max_score(board, board.state)
        return score

    def set_from_yaml(self, yaml_path: str) -> "GlobalAI":
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            settings = yaml_settings['AI']
            self.custom_depth = settings["CUSTOM_DEPTH"]
            self.white_player_str = settings["WHITE_PLAYER"]
            self.black_player_str = settings["BLACK_PLAYER"]
            self.paused = settings["PAUSED"]
            self.set_players(self._create_chess_score(yaml_settings))
        return self
    
    def piece_is_playable(self, is_white: bool) -> bool:
        if is_white:
            return True if self.white_player_str == "PLAYER" else False
        else:
            return True if self.black_player_str == "PLAYER" else False