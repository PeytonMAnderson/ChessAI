"""

    Global Variable Class for tracking Chess Variables

"""
import yaml

from .chess_utils import ChessUtils
from .chess_check import ChessCheck
from .chess_moves import ChessMoves
from .chess_base_moves import ChessBaseMoves
from .chess_board import ChessBoard
from .chess_history import ChessHistory
from .chess_state import ChessState

#Global Variable Class
class GlobalChess:
    def __init__(self,
                 board_files: int = 8,
                 board_ranks: int = 8,
                 board: list =  [],
                 piece_numbers: dict = {},
    *args, **kwargs) -> None:
        
        #Attach Chess Objects
        self.board = ChessBoard(board, board_ranks, board_files, piece_numbers)
        self.util = ChessUtils()
        self.history = ChessHistory()
        self.base_moves = ChessBaseMoves(self.util, self.board)
        self.check = ChessCheck(self.util, self.board, self.base_moves)
        self.moves = ChessMoves(self.util, self.board, self.base_moves, self.check)
        self.state = ChessState()

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
        new_move = self.moves.move(rank_i_old, file_i_old, rank_i_new, file_i_new, self.board.board, self.state.whites_turn)
        new_hist = {"last_move": new_move['move_str'], "fen_string": new_move['fen_string']}
        print(new_hist)
        self.board.board = new_move['board']
        self.state.update_from_move_dict(new_move)
        self.history.pop_add(new_hist)        
        self.state.last_move = new_move['move_str']

    def set_from_yaml(self, yaml_path: str) -> "GlobalChess":
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            settings = yaml_settings['CHESS']

            #Save Board Chess Values
            self.board.files = settings['BOARD_FILES']
            self.board.ranks = settings['BOARD_RANKS']
            self.board.piece_numbers = settings['PIECE_NUMBERS']

            #Get Chess State from FEN string
            fen_data = self.util.convert_fen_to_board(settings['BOARD'], self.board.files, self.board.ranks, self.board.piece_numbers)
            self.board.board = fen_data[0]
            self.state.update_from_fen_list(fen_data)
            self.history.pop_add({"last_move": None, "fen_string": settings['BOARD']})

        return self