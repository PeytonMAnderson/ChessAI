

from .chess_utils import ChessUtils
from .chess_board import ChessBoard
from .chess_base_moves import ChessBaseMoves

class ChessEnpassant:
    def __init__(self, utils: ChessUtils, board: ChessBoard, base_moves: ChessBaseMoves, *args, **kwargs) -> None:
        self.utils = utils
        self.board = board
        self.base_moves = base_moves

    def is_move_enpassant(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> bool:
        piece_value = self.utils.get_piece_number_on_board(rank_i_old, file_i_old, board, self.board.files)
        piece_type = self.utils.get_str_from_piece_type(piece_value, self.board.piece_numbers, True)
        if piece_type != 'P':
            return False
        rank_diff = rank_i_new - rank_i_old
        if abs(rank_diff) == 2:
            return True
        
    def get_enpassant_str(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> str:
        if self.is_move_enpassant(rank_i_old, file_i_old, rank_i_new, file_i_new, board):
            r_diff = int((rank_i_new - rank_i_old)/2)
            rank = self.utils.get_rank_from_number(rank_i_old + r_diff, self.board.ranks)
            file = self.utils.get_file_from_number(file_i_old)
            return file + rank
        else:
            return "-"
    
    def get_enpassant_moves(self, rank_i_old: int, file_i_old: int, board: list, enpassant: str) -> list:
        piece_value = self.utils.get_piece_number_on_board(rank_i_old, file_i_old, board, self.board.files)
        piece_type = self.utils.get_str_from_piece_type(piece_value, self.board.piece_numbers, True)
        if piece_type != 'P' or enpassant == '-':
            return []
        is_white = self.utils.get_is_white_from_piece_number(piece_value, self.board.piece_numbers)
        e_pos = self.utils.get_position_from_rank_file(enpassant, self.board.ranks)
        if e_pos is None:
            return []
        pawn_attack_moves = self.base_moves.get_pawn_attack_moves(rank_i_old, file_i_old, is_white)
        for ra, fa in pawn_attack_moves:
            if (ra, fa) == (e_pos[0], e_pos[1]):
                if self.base_moves.check_if_open(rank_i_old, file_i_old, e_pos[0], e_pos[1], board):
                    return [(e_pos[0], e_pos[1])]
        return []
    
    def move_is_enpassant(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list, enpassant: str) -> bool:
        piece_value = self.utils.get_piece_number_on_board(rank_i_old, file_i_old, board, self.board.files)
        piece_type = self.utils.get_str_from_piece_type(piece_value, self.board.piece_numbers, True)
        if piece_type != 'P':
            return False
        e_pos = self.utils.get_position_from_rank_file(enpassant, self.board.ranks)
        if e_pos is None:
            return False
        if (rank_i_new, file_i_new) == (e_pos[0], e_pos[1]):
            return True
        return False
    
    def take_pawn(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> None:
        r, f = rank_i_old, file_i_new
        pawn_pos = r * self.board.files + f
        board[pawn_pos] = 0
