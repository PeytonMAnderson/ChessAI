
from .chess_board import ChessBoard
from .chess_utils import ChessUtils

class ChessPromotion:
    def __init__(self, utils: ChessUtils, board: ChessBoard, *args, **kwargs) -> None:
        self.utils = utils
        self.board = board

    def is_promotion(self, rank_i_new: int) -> bool:
        if rank_i_new == 0 or rank_i_new == len(self.board.ranks) - 1:
            return True
        return False
    
    def move_can_promote(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> bool:
        piece_value = self.utils.get_piece_number_on_board(rank_i_old, file_i_old, board, self.board.files)
        piece_type = self.utils.get_str_from_piece_number(piece_value, self.board.piece_numbers)
        if piece_type == "P":
            if rank_i_new == 0:
                return True
        elif piece_type == "p":
            if rank_i_new == self.board.ranks - 1:
                return True
        else:
            return False