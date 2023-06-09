import yaml

from .base_ai import BaseAI
from .custom_ai.custom_ai import CustomAI

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

    def set_players(self):
        self.white_player = self.get_player_from_str(self.white_player_str, True)
        self.black_player = self.get_player_from_str(self.black_player_str, False)

    def execute_player(self, player_str: str, player_value: BaseAI | None, board: list, env): 
        if player_str == "PLAYER":
            return
        elif player_str == "CUSTOM":
            player_value.execute_turn(board, env)
        
    def execute_turn(self, whites_turn: bool, board: list, env): 

        if self.paused is True or env.chess.state.check_status == 'White Checkmate' or env.chess.state.check_status == 'Black Checkmate':
            return
        if whites_turn:
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