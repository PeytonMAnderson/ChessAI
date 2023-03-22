"""

    Global Variable Class for tracking Chess Variables

"""
import yaml

from .chess_utils import ChessUtils
from .chess_board import ChessBoard
from .chess_history import ChessHistory

#Global Variable Class
class GlobalChess:
    def __init__(self,
                 board_files: int = 8,
                 board_ranks: int = 8,
                 piece_numbers: dict = {},
                 piece_scores: dict = {},
    *args, **kwargs) -> None:
        
        #Attach Chess Objects
        self.board = ChessBoard(piece_numbers, piece_scores, board_ranks, board_files)
        self.history = ChessHistory()
        self.last_move_str = "None"
        self.last_move_tuple = None
        self.game_ended = False
        
    def move_piece(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int) -> "GlobalChess":
        """Move a piece on the chess board.
            Updates History.
            Updates Board.
            Updates turn.
            Updates castle availability.
            Updates En Passant Availability
            Updates half moves.
            Updates full moves.

            Returns: Self for chaining
        """
        if self.game_ended:
            return
        
        self.board.move_piece(rank_i_old, file_i_old, rank_i_new, file_i_new)
        new_fen = self.board.board_to_fen()
        new_hist = {"last_move_str": "TODO", "last_move_tuple": (0,0, 0,1), "fen_string": new_fen}
        self.last_move_str = new_hist['last_move_str']
        self.last_move_tuple = new_hist['last_move_tuple']
        self.history.pop_add(new_hist)

        print(f"New Move: {self.last_move_str}")
        print(f"New FEN: {new_fen}")

    def load_from_history(self, frame: dict) -> "GlobalChess":
        self.board.fen_to_board(frame['fen_string'])
        self.last_move_str = frame['last_move_str']
        self.last_move_tuple = frame['last_move_tuple']

    def set_from_yaml(self, yaml_path: str) -> "GlobalChess":
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            settings = yaml_settings['CHESS']

            #Save Board Chess Values
            self.board.files = settings['BOARD_FILES']
            self.board.ranks = settings['BOARD_RANKS']
            self.board.utils.piece_values = settings['PIECE_VALUES']
            self.board.utils.piece_scores = settings['PIECE_SCORES']
            self.board.fen_to_board(settings['BOARD'])
            self.board.max_half_moves = settings['MAX_HALF_MOVES']

            #Start history
            self.history.pop_add({"last_move_str": "None", "last_move_tuple": None, "fen_string": settings['BOARD']})
        return self