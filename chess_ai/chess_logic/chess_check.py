
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
    
    def calc_check_status(self, board: list, whites_turn: bool) -> str:
        """Calculates check status of the game.

            This includes:

                Check
                Checkmate
                Stalemate
            
            Return str of the check status
        """
        white_king = self.utils.get_piece_number_from_str('K', self.board.piece_numbers)
        black_king = self.utils.get_piece_number_from_str('k', self.board.piece_numbers)

        white_check = self.check_for_check(white_king, board)
        black_check = self.check_for_check(black_king, board)

        white_moves = self.check_all_available_moves(True, board)
        black_moves = self.check_all_available_moves(False, board)

        check_status = "None"
        if white_check:
            if len(white_moves) == 0:
                check_status = "Black Checkmate"
            else:
                check_status = "Black Check"
        elif black_check:
            if len(black_moves) == 0:
                check_status = "White Checkmate"
            else:
                check_status = "White Check"
        else:
            if whites_turn and len(white_moves) == 0:
                check_status = "Black Stalemate"
            elif not whites_turn and len(black_moves) == 0:
                check_status = "White Stalemate"
                
        return check_status