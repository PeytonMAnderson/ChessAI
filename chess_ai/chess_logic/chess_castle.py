
from .chess_board import ChessBoard
from .chess_utils import ChessUtils
from .chess_base_moves import ChessBaseMoves
from .chess_check import ChessCheck

class ChessCastle:
    def __init__(self, utils: ChessUtils, board: ChessBoard, base_move: ChessBaseMoves, check: ChessCheck, *args, **kwargs) -> None:
        self.utils = utils
        self.board = board
        self.base_moves = base_move
        self.check = check

    def get_castle_side(self, file_i_old: int, file_i_new: int) -> str:
        return "K" if file_i_old < file_i_new else "Q"

    def get_castle_locations(self, rank_i_old: int, file_i_old: int, board: list, castle_avail: str, is_white: bool) -> list:
        valid_moves = []
        king = 'K' if is_white else 'k'
        queen = 'Q' if is_white else 'q'
        if castle_avail.count(king) > 0:
            valid_moves.append((rank_i_old, file_i_old + 2))
        if castle_avail.count(queen) > 0:
            valid_moves.append((rank_i_old, file_i_old - 2))
        return valid_moves
    
    def filter_open_to_rook(self, rank_i_old: int, file_i_old: int, board: list, move_list: list, is_white: bool) -> list:
        rook_str = "R" if is_white else "r"
        valid_moves = []
        for r_new, f_new in move_list:
            #King side
            f = file_i_old
            if f_new > file_i_old:
                while f < self.board.files:
                    f += 1
                    #If open all the way to rook, keep move
                    if self.utils.get_str_from_piece_number(self.utils.get_piece_number_on_board(rank_i_old, f, board, self.board.files), self.board.piece_numbers) == rook_str:
                        valid_moves.append((r_new, f_new))
                    
                    #If blocked at some point between rook, break
                    if self.base_moves.check_if_blocked(rank_i_old, f, board) is True or self.base_moves.check_if_in_bounds(rank_i_old, f) is False:
                        break
            #Queen side
            elif f_new < file_i_old:
                while f > 0:
                    f -= 1
                    #If open all the way to rook, keep move
                    if self.utils.get_str_from_piece_number(self.utils.get_piece_number_on_board(rank_i_old, f, board, self.board.files), self.board.piece_numbers) == rook_str:
                        valid_moves.append((r_new, f_new))
                    
                    #If blocked at some point between rook, break
                    if self.base_moves.check_if_blocked(rank_i_old, f, board) is True or self.base_moves.check_if_in_bounds(rank_i_old, f) is False:
                        break
        return valid_moves
    
    def filter_castle_check(self, rank_i_old: int, file_i_old: int, board: list, move_list: list, is_white: bool, king_value: int) -> list:
        if self.check.check_for_check(king_value, board):
            return []
        valid_list = []
        for r, f in move_list:
            side = self.get_castle_side(file_i_old, f)
            if side == "K":
                if self.check.check_move_cause_check(rank_i_old, file_i_old, r, f - 1, board) is False:
                    valid_list.append((r, f))
            if side == "Q":
                if self.check.check_move_cause_check(rank_i_old, file_i_old, r, f + 1, board) is False:
                    valid_list.append((r, f))
        return valid_list

    def get_castle_moves(self, rank_i_old: int, file_i_old: int, board: list, castle_avail: str) -> list:
        piece_value = self.utils.get_piece_number_on_board(rank_i_old, file_i_old, board, self.board.files)
        piece_type = self.utils.get_str_from_piece_type(piece_value, self.board.piece_numbers, True)
        if piece_type != 'K':
            return []
        is_white = self.utils.get_is_white_from_piece_number(piece_value, self.board.piece_numbers)
        all_moves = self.get_castle_locations(rank_i_old, file_i_old, board, castle_avail, is_white)
        open_moves = self.filter_open_to_rook(rank_i_old, file_i_old, board, all_moves, is_white)
        return self.filter_castle_check(rank_i_old, file_i_old, board, open_moves, is_white, piece_value)
    
    def move_is_castle(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> bool:
        piece_value = self.utils.get_piece_number_on_board(rank_i_old, file_i_old, board, self.board.files)
        piece_type = self.utils.get_str_from_piece_type(piece_value, self.board.piece_numbers, True)
        if piece_type != 'K':
            return False
        diff_f = file_i_new - file_i_old
        if diff_f == 2 or diff_f == -2:
            return True
        return False

    
    def go_to_rook(self, rank_i_old: int, file_i_old: int, board: list, side: str) -> tuple:
        r, f = rank_i_old, file_i_old
        dir = 1 if side == "K" else -1
        while f < self.board.files - 1 and f > 0:
            f += dir
            if self.utils.get_str_from_piece_type(self.utils.get_piece_number_on_board(r, f, board, self.board.files), self.board.piece_numbers, True) == "R":
                return r, f
        print("WARNING: Unable to find rook when it should be there.")
        return r, f
            
    def get_rook_position_old(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> tuple:
        side = self.get_castle_side(file_i_old, file_i_new)
        return self.go_to_rook(rank_i_old, file_i_old, board, side)
    
    def get_rook_position_new(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> tuple:
        side = self.get_castle_side(file_i_old, file_i_new)
        if side == "K":
            return rank_i_old, file_i_new - 1
        else:
            return rank_i_old, file_i_new + 1
        
    def get_castle_str(self, file_i_old: int, file_i_new: int) -> str:
        side = self.get_castle_side(file_i_old, file_i_new)
        if side == "K":
            return "O-O"
        else:
            return "O-O-O"
    
    def update_avail(self, rank_i_old: int, file_i_old: int, board: list, castle_avail: str) -> list:
        piece_value = self.utils.get_piece_number_on_board(rank_i_old, file_i_old, board, self.board.files)
        piece_type = self.utils.get_str_from_piece_number(piece_value, self.board.piece_numbers)

        #If any other piece moved
        if piece_type != 'K' and piece_type != 'k' and piece_type != 'R' and piece_type != 'r':
            return castle_avail
        
        #If King Moved
        if piece_type == 'K':
            new_str = castle_avail
            if new_str.count('K') > 0:
                new_str = new_str.replace('K', '')
            if new_str.count('Q') > 0:
                new_str = new_str.replace('Q', '')
            return new_str
        elif piece_type == 'k':
            new_str = castle_avail
            if new_str.count('k') > 0:
                new_str = new_str.replace('k', '')
            if new_str.count('q') > 0:
                new_str = new_str.replace('q', '')
            return new_str
        
        #If rook moved
        elif piece_type == 'R':
            king_value = self.utils.get_piece_number_from_str('K', self.board.piece_numbers)
            kr, kf = self.board.get_piece_position(king_value, board)
            #King side
            if kf < file_i_old:
                if castle_avail.count('K') > 0:
                    return castle_avail.replace('K', '')
            else:
                if castle_avail.count('Q') > 0:
                    return castle_avail.replace('Q', '')
        elif piece_type == 'r':
            king_value = self.utils.get_piece_number_from_str('r', self.board.piece_numbers)
            kr, kf = self.board.get_piece_position(king_value, board)
            #King side
            if kf < file_i_old:
                if castle_avail.count('k') > 0:
                    return castle_avail.replace('k', '')
            else:
                if castle_avail.count('q') > 0:
                    return castle_avail.replace('q', '')
        return castle_avail