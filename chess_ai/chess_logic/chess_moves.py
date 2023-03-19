
from .chess_utils import ChessUtils
from .chess_board import ChessBoard
from .chess_base_moves import ChessBaseMoves
from .chess_check import ChessCheck

class ChessMoves:
    def __init__(self, utils: ChessUtils, board: ChessBoard, base_move: ChessBaseMoves, check: ChessCheck, *args, **kwargs) -> None:
        self.utils = utils
        self.board = board
        self.base_move = base_move
        self.check = check

    def filter_moves(self, rank_i_old: int, file_i_old: int, move_list: list, board: list) -> list:
        """Filters all the moves passed in the move_list. If a move causes check, the move is dropped.

            Returns: New filtered list of moves.
        """
        filtered_moves = []
        for new_r, new_f in move_list:
            if self.check.check_move_cause_check(rank_i_old, file_i_old, new_r, new_f, board) is False:
                filtered_moves.append((new_r, new_f))
        return filtered_moves

    def get_valid_moves(self, rank_i_old: int, file_i_old: int, board: list) -> list:
        """Get a list of all valid moves that pass all checks.

            Returns: List of all valid moves.
        """
        piece_function = self.base_move.get_piece_type_function(rank_i_old, file_i_old, board)
        if piece_function is not None:
            moves = piece_function(rank_i_old, file_i_old, board)
            if moves is not None:
                return self.filter_moves(rank_i_old, file_i_old, moves)
            print("WARNING: Moves does not exist.")
        else:
            print("WARNING: Piece function does not exist.")
        return []

    def get_move_str(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list) -> str:
        """Get the move string of the passed move (rank_i_old, file_i_old) -> (rank_i_new, file_i_new).

            Returns: Move String.
        """
        board_position_old = rank_i_old * self.board.files + file_i_old
        board_position_new = rank_i_new * self.board.files + file_i_new

        #Get the pieces that are moving and the captured piece
        moving_piece = board[board_position_old]
        destination_piece = board[board_position_new]

        #Determin if a capture happened
        capture_string = ""
        if destination_piece != 0:
            capture_string = "x"

        #Get the destination rank and file
        destination_rank_str: str = str(self.board.ranks - rank_i_new)
        destination_file_str: str = self.utils.get_file_from_number(file_i_new)
        moving_piece_file_str: str = ''
        moving_piece_str: str = self.utils.get_str_from_piece_type(moving_piece, self.board.piece_numbers, True)

        #Show file from for certain cases
        if moving_piece_str == 'P' and capture_string == 'x':
            moving_piece_file_str = self.get_file_from_number(file_i_old)

        #Remove the P if it was a Pawn
        if moving_piece_str == 'P':
            moving_piece_str = ''

        #Return the entire Move string
        return moving_piece_file_str + moving_piece_str + capture_string + destination_file_str + destination_rank_str

    def get_position_from_move_str(self, move_str: str) -> tuple | None:
        """Get Position on board from the move string. If move string is None, return None.

            Returns: ( rank_i, file_i )
        """
        if move_str is None:
            return None
        rank = move_str[len(move_str)-1]
        file = move_str[len(move_str)-2]
        file_i = self.utils.get_number_from_file(file)
        rank_i = self.utils.get_number_from_rank(rank)
        return rank_i, file_i

    def move(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list, whits_turn: bool) -> dict | None:
        """ Moves the piece on the passed board.

            Gets the new Move string.
            Updates turn.
            Updates castle availability.
            Updates En Passant Availability
            Updates half moves.
            Updates full moves.
            Generates new FEN String.

            Returns: dict[  "board"   "whites_turn"     "fen_string"   "castle_avail"    "en_passant"    "half_move"    "full_move"    ] or None if no move.
        """
        board_position_old = rank_i_old * self.board.files + file_i_old
        board_position_new = rank_i_new * self.board.files + file_i_new

        if board_position_old < len(board) and board_position_new < len(board):
            
            #Get Move String
            new_move = self.get_move_str(rank_i_old, file_i_old, rank_i_new, file_i_new, board)

            #Update Piece on board
            new_board = board.copy()
            new_board[board_position_new] = new_board[board_position_old]
            new_board[board_position_old] = 0

            #Update Turn
            whites_turn = False if whits_turn else True

            #Get Castle Availability
            castle_avail = 'KQkq'

            #Get En Passant Availability
            en_passant = '-'

            #Get Half Move
            half_move = 0

            #Get Full Move
            full_move = 1

            #Get New FEN String
            new_fen = self.utils.convert_board_to_fen(board,
                                                        whites_turn,
                                                        castle_avail,
                                                        en_passant,
                                                        half_move,
                                                        full_move,
                                                        self.board.files,
                                                        self.board.ranks, 
                                                        self.board.piece_numbers)
            
            print(f"New Move: {new_move}")
            print(f"New FEN: {new_fen}")
            return {
                "board": new_board,
                "whites_turn": whites_turn,
                "fen_string": new_fen,
                "castle_avail": castle_avail,
                "en_passant": en_passant,
                "half_move": half_move,
                "full_move": full_move
            }

        return None