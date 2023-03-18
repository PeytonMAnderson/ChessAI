"""

    Global Variable Class for tracking Chess Variables

"""
import yaml

from .chess_utils import convert_fen_to_board

#Global Variable Class
class GlobalChess:
    def __init__(self,
                 board_files: int = 8,
                 board_ranks: int = 8,
                 board: list =  [],
                 piece_numbers: dict = {},
    *args, **kwargs) -> None:
        self.board_files = board_files
        self.board_ranks = board_ranks
        self.board = board
        self.history = []
        self.history_position = 0
        self.piece_numbers = piece_numbers
        self.valid_moves = []
        self.all_valid_moves = []
        self.whites_turn = True

    def set_from_yaml(self, yaml_path: str) -> "GlobalChess":
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            settings = yaml_settings['CHESS']

            #Save Chess Values
            self.board_files = settings['BOARD_FILES']
            self.board_ranks = settings['BOARD_RANKS']
            self.piece_numbers = settings['PIECE_NUMBERS']

            #Get Chess State from FEN string
            fen_data = convert_fen_to_board(settings['BOARD'], self.board_files, self.board_ranks, self.piece_numbers)
            self.board = fen_data[0]
            self.whites_turn = fen_data[1]

            self.history.append((None, settings['BOARD']))

        return self