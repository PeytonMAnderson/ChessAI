
from .chess_board import ChessBoard
from .chess_utils import ChessUtils
from .chess_base_moves import ChessBaseMoves


class ChessCheck:
    def __init__(self, utils: ChessUtils, board: ChessBoard, base_move: ChessBaseMoves, *args, **kwargs) -> None:
        self.utils = utils
        self.board = board
        self.base_moves = base_move

    def get_king_position(self, king_value, board: list) -> tuple | None:
        """Get the kings rank and file by checking the board in the parameters.

            Returns: tuple[rank_i, file_i] of the king location. None if king is not found.
        """
        rank_i = 0
        file_i = 0
        for piece in board:
            if piece == king_value:
                return rank_i, file_i
            if file_i >= self.board.files - 1:
                rank_i += 1
                file_i = 0
            else:
                file_i += 1
        return None

    def get_piece_values_for_color(self, is_white: bool) -> list:
        """Get the Piece Numbers of all pieces in the team based off is_white.

            Returns: List of Piece Numbers.
        """
        piece_values = []
        piece_types_black = ['p', 'n', 'b', 'r', 'q', 'k']
        piece_types_white = ['P', 'N', 'B', 'R', 'Q', 'K']
        types = piece_types_white if is_white else piece_types_black
        for type in types:
            piece_values.append(self.utils.get_piece_number_from_str(type, self.board.piece_numbers))
        return piece_values

    def get_all_piece_locations(self, is_white: bool, board: list) -> list:
        """Get the locations of all pieces apart of the team based of is_white on the local board.

            Returns: List of locations (rank_i, file_i) of all pieces.
        """
        pieces_list = []
        piece_types = self.get_piece_values_for_color(is_white)
        rank_i = 0
        file_i = 0
        for piece in board:
            if piece_types.count(piece):
                pieces_list.append((rank_i, file_i))
            if file_i >= self.board.files - 1:
                rank_i += 1
                file_i = 0
            else:
                file_i += 1
        return pieces_list

    def get_all_moves(self, is_white: bool, board: list) -> list:
        """Get all the moves for all pieces on a team.

            Returns: List of all moves (rank_i, file_i) for all pieces on team.
        """
        pieces_list = self.get_all_piece_locations(is_white, board)
        moves_list = []
        for piece_r, piece_f in pieces_list:
            moves_list = moves_list + self.base_moves.get_base_moves(piece_r, piece_f, board)
        return moves_list        

    def check_all_moves_for_check(self, rank_i: int, file_i: int, is_white: bool, board: list) -> bool:
        """Check all moves of other team to see if they cause check for passed king location (rank_i, file_i).

            Returns: True if the king (rank_i, file_i) is in check, false if otherwise.
        """
        moves_list = self.get_all_moves( not is_white, board)
        for move in moves_list:
            if move == (rank_i, file_i):
                return True
        return False
    
    def check_for_check(self, king_value: int, board: list) -> bool:
        """Check for check of king_value king from the passed board.

            Returns: True if the king is in check, false if otherwise.
        """
        king_pos = self.get_king_position(king_value, board)
        is_white = self.utils.get_is_white_from_piece_number(king_value, self.board.piece_numbers)
        if king_pos is not None:
            return self.check_all_moves_for_check(king_pos[0], king_pos[1], is_white, board)
        print("WARNING: Unable to determine King Position")
        return False

    def check_move_cause_check(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> bool:
        """Check if a new move (rank_i_old, file_i_old) -> (rank_i_new, file_i_new) will cause a check on the player's king from the passed board.

            Returns: True if the move will cause a check, false if otherwise.
        """
        new_board = self.base_moves.base_move(rank_i_old, file_i_old, rank_i_new, file_i_new, board)
        moving_piece = board[rank_i_old * self.board.files + file_i_old]
        is_white = self.utils.get_is_white_from_piece_number(moving_piece, self.board.piece_numbers)
        king_value = self.utils.get_piece_number_from_str('K', self.board.piece_numbers) if is_white else self.utils.get_piece_number_from_str('k', self.board.piece_numbers)
        return self.check_for_check(king_value, new_board)

    def check_all_available_moves(self, is_white: bool, board: list) -> list:
        """Checks all available moves for check. If a move causes a check, it is removed from the list of valid moves.

            Returns: List of moves that do not cause check.
        """
        pieces_list = self.get_all_piece_locations(is_white, board)
        valid_moves = []
        for piece_r, piece_f in pieces_list:
            moves_list = self.base_moves.get_base_moves(piece_r, piece_f, board)
            for move_r, move_f in moves_list:
                if self.check_move_cause_check(piece_r, piece_f, move_r, move_f, board) is False:
                    valid_moves.append((piece_r, piece_f, move_r, move_f))
        return valid_moves
    
    def calc_check_status(self, board: list, whites_turn: bool) -> int | None:
        white_king = self.utils.get_piece_number_from_str('K', self.board.piece_numbers)
        black_king = self.utils.get_piece_number_from_str('k', self.board.piece_numbers)

        white_check = self.check_for_check(white_king, board)
        black_check = self.check_for_check(black_king, board)

        white_moves = self.check_all_available_moves(True, board)
        black_moves = self.check_all_available_moves(False, board)

        check_status = None

        if white_check:
            if len(white_moves) == 0:
                check_status = -2
            else:
                check_status = -1
        elif black_check:
            if len(black_moves) == 0:
                check_status = 2
            else:
                check_status = 1
        else:
            if whites_turn and len(white_moves) == 0:
                check_status = 0
            elif not whites_turn and len(black_moves) == 0:
                check_status = 0
                
        return check_status
    
    def get_king_position_fast(self, king_value, king_is_white: bool, board: list) -> tuple | None:
        """Get the kings rank and file by checking the board in the parameters.

            Returns: tuple[rank_i, file_i] of the king location. None if king is not found.
        """
        rank_i, rank_diff = (0, 1) if not king_is_white else (self.board.ranks - 1, -1)
        while (rank_i >= 0 and rank_i < self.board.ranks):
            file_i = 0
            while file_i < self.board.files:
                if board[rank_i * self.board.files + file_i] == king_value:
                    return rank_i, file_i
                file_i += 1
            rank_i += rank_diff
        return None
    
    def check_piece_moves_cause_check_fast(self, king_rank: int, king_file: int, piece_rank: int, piece_file: int, piece_function: any, board: list) -> bool:
        moves_checked = 0
        piece_moves = piece_function(piece_rank, piece_file, board)
        for new_r, new_f in piece_moves:
            moves_checked += 1
            if (new_r, new_f) == (king_rank, king_file):
                return True
        return False

    
    def check_piece_causes_check_fast(self, king_rank: int, king_file: int, piece_rank: int, piece_file: int, piece_str: str, board: list) -> bool:
        if piece_str == "P":
             if king_file == piece_file - 1 or king_file == piece_file + 1:
                if king_rank == piece_rank - 1 or king_rank == piece_rank + 1:
                    return self.check_piece_moves_cause_check_fast(king_rank, king_file, piece_rank, piece_file, self.base_moves.check_pawn_moves, board)
        elif piece_str == "N":
            if king_file >= piece_file - 2 and king_file <= piece_file + 2:
                if king_rank >= piece_rank - 2 and king_rank <= piece_rank + 2:
                    return self.check_piece_moves_cause_check_fast(king_rank, king_file, piece_rank, piece_file, self.base_moves.check_knight_moves, board)
        elif piece_str == "B":
            if king_rank + king_file == piece_rank + piece_file or king_rank - king_file == piece_rank - piece_file:
                return self.check_piece_moves_cause_check_fast(king_rank, king_file, piece_rank, piece_file, self.base_moves.check_bishop_moves, board)
        elif piece_str == "R":
            if king_file == piece_file or king_rank == piece_rank:
                return self.check_piece_moves_cause_check_fast(king_rank, king_file, piece_rank, piece_file, self.base_moves.check_rook_moves, board)
        elif piece_str == "Q":
            if king_file == piece_file or king_rank == piece_rank or king_rank + king_file == piece_rank + piece_file or king_rank - king_file == piece_rank - piece_file:
                return self.check_piece_moves_cause_check_fast(king_rank, king_file, piece_rank, piece_file, self.base_moves.check_queen_moves, board)
        elif piece_str == "K":
            if king_file >= piece_file - 1 and king_file <= piece_file + 1:
                if king_rank >= piece_rank - 1 and king_rank <= piece_rank + 1:
                    return self.check_piece_moves_cause_check_fast(king_rank, king_file, piece_rank, piece_file, self.base_moves.check_king_moves, board)
        return False

    
    def check_all_moves_for_check_fast(self, king_rank: int, king_file: int, king_is_white: bool, board: list) -> bool:
        rank_i, rank_diff = (0, 1) if king_is_white else (self.board.ranks - 1, -1)
        while (rank_i >= 0 and rank_i < self.board.ranks):
            file_i = 0
            while (file_i < self.board.files):
                piece_str = self.utils.get_str_from_piece_type(board[rank_i * self.board.files + file_i], self.board.piece_numbers, True)
                if piece_str is not None:
                    piece_color = self.utils.get_is_white_from_piece_number(board[rank_i * self.board.files + file_i], self.board.piece_numbers)
                    if piece_color is not king_is_white:
                        if self.check_piece_causes_check_fast(king_rank, king_file, rank_i, file_i, piece_str, board):
                            return True
                file_i += 1
            rank_i += rank_diff
        return False

    
    def check_for_check_fast(self, king_str: str, board: list) -> bool:
        king_value = self.utils.get_piece_number_from_str(king_str, self.board.piece_numbers)
        is_white = True if king_str == 'K' else False
        king_pos = self.get_king_position_fast(king_value, is_white, board)
        if king_pos is not None:
            return self.check_all_moves_for_check_fast(king_pos[0], king_pos[1], is_white, board)
        print("WARNING: Unable to determine King Position")
        return False

    def get_piece_locations_fast(self, king_is_white: bool, board: list) -> list:
        rank_i, rank_diff = 0, 1
        piece_locations = []
        while (rank_i >= 0 and rank_i < self.board.ranks):
            file_i = 0
            while file_i < self.board.files:
                piece_str = self.utils.get_str_from_piece_type(board[rank_i * self.board.files + file_i], self.board.piece_numbers, True)
                if piece_str is not None:
                    piece_color = self.utils.get_is_white_from_piece_number(board[rank_i * self.board.files + file_i], self.board.piece_numbers)
                    if piece_color is king_is_white:
                        piece_locations.append((rank_i, file_i))
                file_i += 1
            rank_i += rank_diff
        return piece_locations 
    
    def filter_related_position_fast(self,  king_rank: int, king_file: int, piece_rank: int, piece_file: int) -> bool:
        return True
        if king_file >= piece_file - 2 and king_file <= piece_file + 2:
            if king_rank >= piece_rank - 2 and king_rank <= piece_rank + 2:
                return True
        elif king_file == piece_file or king_rank == piece_rank or king_rank + king_file == piece_rank + piece_file or king_rank - king_file == piece_rank - piece_file:
            return True
        return False

    def check_move_causes_check_fast(self, king_rank: int, king_file: int, king_is_white: bool, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> bool:
        """Check if a new move (rank_i_old, file_i_old) -> (rank_i_new, file_i_new) will cause a check on the player's king from the passed board.

            Returns: True if the move will cause a check, false if otherwise.
        """
        piece_str = self.utils.get_str_from_piece_type(board[rank_i_old * self.board.files + file_i_old], self.board.piece_numbers, True)
        king_new_rank, king_new_file = (king_rank, king_file) if piece_str != "K" else (rank_i_new, file_i_new)
        if self.check_all_moves_for_check_fast(king_rank, king_file, king_is_white, board):
            if self.filter_related_position_fast(king_rank, king_file, rank_i_old, file_i_old):
                new_board = self.base_moves.base_move(rank_i_old, file_i_old, rank_i_new, file_i_new, board)
                return self.check_all_moves_for_check_fast(king_new_rank, king_new_file, king_is_white, new_board)
            return True
        else:
            if self.filter_related_position_fast(king_rank, king_file, rank_i_new, file_i_new):
                new_board = self.base_moves.base_move(rank_i_old, file_i_old, rank_i_new, file_i_new, board)
                return self.check_all_moves_for_check_fast(king_new_rank, king_new_file, king_is_white, new_board)
            return False
    
    def check_all_available_moves_fast(self, king_rank: int, king_file: int, king_is_white: bool, board: list) -> list:
        """Checks all available moves for check. If a move causes a check, it is removed from the list of valid moves.

            Returns: List of moves that do not cause check.
        """
        pieces_list = self.get_piece_locations_fast(king_is_white, board)
        valid_moves = []
        for piece_r, piece_f in pieces_list:
            moves_list = self.base_moves.get_base_moves(piece_r, piece_f, board)
            for move_r, move_f in moves_list:
                caused_check = self.check_move_causes_check_fast(king_rank, king_file, king_is_white, piece_r, piece_f, move_r, move_f, board)
                if caused_check is False:
                    valid_moves.append((piece_r, piece_f, move_r, move_f))
        return valid_moves
    
    def calc_check_status_fast(self, board: list, whites_turn: bool) -> int | None:
        if whites_turn:
            king_value = self.utils.get_piece_number_from_str('K', self.board.piece_numbers)
            king_pos = self.get_king_position_fast(king_value, True, board)
            if king_pos is not None:
                white_moves = self.check_all_available_moves_fast(king_pos[0], king_pos[1], True, board)
                if self.check_all_moves_for_check_fast(king_pos[0], king_pos[1], True, board):
                    if len(white_moves) == 0:
                        return -2
                    else:
                        return -1
                elif len(white_moves) == 0:
                    return 0
                else:
                    return None
        else:
            king_value = self.utils.get_piece_number_from_str('k', self.board.piece_numbers)
            king_pos = self.get_king_position_fast(king_value, False, board)
            if king_pos is not None:
                black_moves = self.check_all_available_moves_fast(king_pos[0], king_pos[1], False, board)
                if self.check_all_moves_for_check_fast(king_pos[0], king_pos[1], False, board):
                    if len(black_moves) == 0:
                        return 2
                    else:
                        return 1
                elif len(black_moves) == 0:
                    return 0
                else:
                    return None
        print("WARNING: King was not found.")
        return None

    def calc_check_status_str(self, board: list, whites_turn: bool) -> str:
        """Calculates check status of the game.

            This includes:

                Check
                Checkmate
                Stalemate
            
            Return str of the check status
        """
        check_status = self.calc_check_status_fast(board, whites_turn)
        if check_status is None:
            return "None"
        elif check_status == -2:
            return "Black Checkmate"
        elif check_status == -1:
            return "Black Check"
        elif check_status == 0:
            return "Stalemate"
        elif check_status == 1:
            return "White Check"
        elif check_status == 2:
            return "White Checkmate"
    




