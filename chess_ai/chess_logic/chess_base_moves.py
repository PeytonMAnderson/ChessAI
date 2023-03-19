from typing import Callable

from .chess_utils import ChessUtils
from .chess_board import ChessBoard

class ChessBaseMoves:
    def __init__(self, utils: ChessUtils, board: ChessBoard, *args, **kwargs) -> None:
        self.utils = utils
        self.board = board

    def check_if_in_bounds(self, rank_i: int, file_i: int) -> bool:
        """Checks if the new position is located on the board.

            Returns: True if the new position is on the board. False if off the board.
        """
        if rank_i < 0 or rank_i >= self.board.ranks:
            return False
        elif file_i < 0 or file_i >= self.board.files:
            return False
        return True
    
    def check_if_blocked(self, rank_i: int, file_i: int, board: list) -> bool:
        """Checks if the new position already has a piece located at that location.

            Returns: True if there is a piece, false if open.
        """
        piece_value = board[rank_i * self.board.files + file_i]
        if piece_value != 0:
            return True
        else:
            return False
    
    def check_if_capturable(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> bool:
        """Checks if the piece located at (rank_i_new, file_i_new) is currently capturable.

            Returns: True if piece is capturable by (rank_i_old, file_i_old), false if on the same team
        """
        moving_piece_value =  board[rank_i_old * self.board.files + file_i_old]
        captured_piece_value =  board[rank_i_new * self.board.files + file_i_new]
        moving_is_white = True if int(moving_piece_value / 10 ) == self.board.piece_numbers['WHITE'] else False
        captured_is_white = True if int(captured_piece_value / 10 ) == self.board.piece_numbers['WHITE'] else False
        if moving_is_white == captured_is_white:
            return False
        return True

    def check_if_open(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> bool:
        """Checks if new location is in bounds. If it is checks if new location is open.
            If the new location is not blocked, then the spot is open.
            If the new location is blocked, checks if the piece is capturable. If it is then the spot is open.

            Returns True if the spot is open, false if the spot is not open.
        """
        if self.check_if_in_bounds(rank_i_new, file_i_new) is False:
            return False
        if self.check_if_blocked(rank_i_new, file_i_new, board):
            if self.check_if_capturable(rank_i_old, file_i_old, rank_i_new, file_i_new, board):
                return True
            else:
                return False
        else:
            return True
    
    def get_pawn_attack_moves(self, rank_i_old: int, file_i_old: int, is_white: bool) -> list:
        """Get the attacking moves for pawn of a certain color.

            Returns: List of moves the pawn is able to attack.
        """
        if is_white:
            return [(rank_i_old - 1, file_i_old - 1), (rank_i_old - 1, file_i_old + 1)]
        return [(rank_i_old + 1, file_i_old - 1), (rank_i_old + 1, file_i_old + 1)]


    def check_pawn_moves(self, rank_i_old: int, file_i_old: int, board: list) -> list:
        """Checks all available moves for the type of PAWN.

            Returns: A list of all available moves: (rank, file) pairs
        """
        piece_value = board[rank_i_old * self.board.files + file_i_old]
        valid_moves = []

        #Add Basic Move
        is_white = self.utils.get_is_white_from_piece_number(piece_value, self.board.piece_numbers)
        new_rank_diff = -1 if is_white else 1
        if is_white:
            if self.check_if_blocked(rank_i_old + new_rank_diff, file_i_old, board) is False:
                valid_moves.append((rank_i_old + new_rank_diff, file_i_old))
        else:
            if self.check_if_blocked(rank_i_old + new_rank_diff, file_i_old, board) is False:
                valid_moves.append((rank_i_old + new_rank_diff, file_i_old))

        #Add Pawn Attacking Moves
        pawn_attack_moves = self.get_pawn_attack_moves(rank_i_old, file_i_old, is_white)
        for new_r, new_f in pawn_attack_moves:
            if self.check_if_blocked(new_r, new_f, board) is True and self.check_if_in_bounds(new_r, new_f) is True:
                if self.check_if_capturable(rank_i_old, file_i_old, new_r, new_f, board):
                    valid_moves.append((new_r, new_f))

        #Add Starting double move
        if rank_i_old == 1 and not is_white:
            if self.check_if_blocked(rank_i_old + 2, file_i_old, board) is False and self.check_if_blocked(rank_i_old + 1, file_i_old, board) is False:
                valid_moves.append((rank_i_old + 2, file_i_old))
        elif rank_i_old == self.board.ranks - 2 and is_white:
            if self.check_if_blocked(rank_i_old - 2, file_i_old, board) is False and self.check_if_blocked(rank_i_old - 1, file_i_old, board) is False:
                valid_moves.append((rank_i_old - 2, file_i_old))

        return valid_moves

    def check_knight_moves(self, rank_i_old: int, file_i_old: int, board: list) -> list:
        """Checks all available moves for the type of KNIGHT.

            Returns: A list of all available moves: (rank, file) pairs
        """
        valid_moves = []

        #Check      top right,     top left,      bottom_right,     bottom_left
        checks = [(2,1), (1,2), (2,-1), (1,-2), (-2,1), (-1,2), (-2,-1), (-1,-2)]

        #Loop through all checks
        for r_d, f_d in checks:
            r, f = rank_i_old + r_d, file_i_old + f_d
            if self.check_if_open(rank_i_old, file_i_old, r, f, board):
                valid_moves.append((r, f))
        return valid_moves


    def check_bishop_moves(self, rank_i_old: int, file_i_old: int, board: list) ->list:
        """Checks all available moves for the type of BISHOP.

            Returns: A list of all available moves: (rank, file) pairs
        """
        valid_moves = []

        #Check top right, top left, bottom_right, bottom_left
        checks = [(1,1), (1,-1), (-1,1), (-1,-1)]

        #Loop through all checks
        for r_d, f_d in checks:
            blocked = False
            r, f = rank_i_old, file_i_old
            while blocked is False:
                r = r + r_d
                f = f + f_d
                if self.check_if_in_bounds(r, f) is False:
                    blocked = True
                elif self.check_if_blocked(r, f, board):
                    if self.check_if_capturable(rank_i_old, file_i_old, r, f, board):
                        valid_moves.append((r, f))
                    blocked = True
                else:
                    valid_moves.append((r, f))

        return valid_moves

    def check_rook_moves(self, rank_i_old: int, file_i_old: int, board: list) -> list:
        """Checks all available moves for the type of ROOK.

            Returns: A list of all available moves: (rank, file) pairs
        """
        valid_moves = []

        #Check right, left, top, bottom
        checks = [(0,1), (0,-1), (1,0), (-1,0)]

        #Loop through all checks
        for r_d, f_d in checks:
            blocked = False
            r, f = rank_i_old, file_i_old
            while blocked is False:
                r = r + r_d
                f = f + f_d
                if self.check_if_in_bounds(r, f) is False:
                    blocked = True
                elif self.check_if_blocked(r, f, board):
                    if self.check_if_capturable(rank_i_old, file_i_old, r, f, board):
                        valid_moves.append((r, f))
                    blocked = True
                else:
                    valid_moves.append((r, f))

        return valid_moves

    def check_queen_moves(self, rank_i_old: int, file_i_old: int, board: list):
        """Checks all available moves for the type of QUEEN.

            Returns: A list of all available moves: (rank, file) pairs
        """
        bishop_moves = self.check_bishop_moves(rank_i_old, file_i_old, board)
        rook_moves = self.check_rook_moves(rank_i_old, file_i_old, board)
        return bishop_moves + rook_moves


    def check_king_moves(self, rank_i_old: int, file_i_old: int, board: list):
        """Checks all available moves for the type of KING.

            Returns: A list of all available moves: (rank, file) pairs
        """
        valid_moves = []

        ro, fo = rank_i_old - 1, file_i_old - 1
        for ri in range(3):
            for fi in range(3):
                r, f = ro + ri, fo + fi
                if self.check_if_open(rank_i_old, file_i_old, r, f, board):
                    valid_moves.append((r, f))
        return valid_moves

    def get_piece_type_function(self, rank_i_old: int, file_i_old: int, board: list) -> Callable | None:
        """Checks they type of piece located at (rank_i_old, file_i_old) and determines which types of move check function to return.

            Returns: Check Moves Function specific to the type of piece at (rank_i_old, file_i_old)
        """
        piece_value = board[rank_i_old * self.board.files + file_i_old]
        if piece_value % 10 == self.board.piece_numbers['NONE']:
            return None
        elif piece_value % 10 == self.board.piece_numbers['PAWN']:
            return self.check_pawn_moves
        elif piece_value % 10 == self.board.piece_numbers['KNIGHT']:
            return self.check_knight_moves
        elif piece_value % 10 == self.board.piece_numbers['BISHOP']:
            return self.check_bishop_moves
        elif piece_value % 10 == self.board.piece_numbers['ROOK']:
            return self.check_rook_moves
        elif piece_value % 10 == self.board.piece_numbers['QUEEN']:
            return self.check_queen_moves
        elif piece_value % 10 == self.board.piece_numbers['KING']:
            return self.check_king_moves
        else:
            return None
    
    def get_base_moves(self, rank_i_old: int, file_i_old: int, board: list) -> list:
        """Gets All Base Moves for Piece located at (rank_i_old, file_i_old).

            Returns: List of all available base moves. Does not account for check and other features. 
        """
        piece_function = self.get_piece_type_function(rank_i_old, file_i_old, board)
        if piece_function is not None:
            valid_moves = piece_function(rank_i_old, file_i_old, board)
            if valid_moves is not None:
                return valid_moves
        return []

    def base_move(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> list:
        """Moves a piece on a given board. Does not update global board.

            Returns: New board with the piece moved.
        """
        board_position_old = rank_i_old * self.board.files + file_i_old
        board_position_new = rank_i_new * self.board.files + file_i_new
        new_board = board.copy()
        if board_position_old < len(new_board) and board_position_new < len(new_board):
            new_board[board_position_new] = new_board[board_position_old]
            new_board[board_position_old] = 0
        return new_board