import yaml

from .base_ai import BaseAI
from ..chess_logic.chess_board import ChessBoard

from .custom_ai.custom import CustomAI
from .stockfish.stock_ai import StockFishAI
from .random.random_ai import RandomAI

class GlobalAI:
    def __init__(self,
          custom_depth: int = 0,
          white_player_str: str = "PLAYER",
          black_player_str: str = "PLAYER",
          paused: bool = False,  
    *args, **kwargs) -> None:
        self.custom_depth = custom_depth
        self.white_player_str = white_player_str
        self.black_player_str = black_player_str
        self.white_player = None
        self.black_player = None
        self.paused = paused

    def get_player_from_str(self, player_str: str, is_white: bool) -> None:
        if player_str == "PLAYER":
            return None
        elif player_str == "CUSTOM":
            return CustomAI(is_white, self.custom_depth)
        elif player_str == "STOCKFISH":
            return StockFishAI(is_white)
        elif player_str == "RANDOM":
            return RandomAI(is_white)

    def set_players(self):
        self.white_player = self.get_player_from_str(self.white_player_str, True)
        self.black_player = self.get_player_from_str(self.black_player_str, False)

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

    def set_from_yaml(self, yaml_path: str) -> "GlobalAI":
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            settings = yaml_settings['AI']
            self.custom_depth = settings["CUSTOM_DEPTH"]
            self.white_player_str = settings["WHITE_PLAYER"]
            self.black_player_str = settings["BLACK_PLAYER"]
            self.paused = settings["PAUSED"]
            self.set_players()
        return self
    
    def piece_is_playable(self, is_white: bool) -> bool:
        if is_white:
            return True if self.white_player_str == "PLAYER" else False
        else:
            return True if self.black_player_str == "PLAYER" else False