
from .chess_utils import ChessUtils
from .chess_board import ChessBoard
from .chess_base_moves import ChessBaseMoves
from .chess_check import ChessCheck
from .chess_castle import ChessCastle
from .chess_enpassant import ChessEnpassant

class ChessMoves:
    def __init__(self, utils: ChessUtils, board: ChessBoard, base_move: ChessBaseMoves, check: ChessCheck, castle: ChessCastle, enpassant: ChessEnpassant, *args, **kwargs) -> None:
        self.utils = utils
        self.board = board
        self.base_move = base_move
        self.check = check
        self.castle = castle
        self.enpassant = enpassant
        self._valid_moves = []

    def filter_moves(self, rank_i_old: int, file_i_old: int, move_list: list, board: list) -> list:
        """Filters all the moves passed in the move_list. If a move causes check, the move is dropped.

            Returns: New filtered list of moves.
        """
        filtered_moves = []
        for new_r, new_f in move_list:
            if self.check.check_move_cause_check(rank_i_old, file_i_old, new_r, new_f, board) is False:
                filtered_moves.append((new_r, new_f))
        return filtered_moves
    
    def get_valid_moves(self, rank_i_old: int, file_i_old: int, board: list, castle_avail: str, enpassant: str) -> list:
        """Get a list of all valid moves that pass all checks.

            Returns: List of all valid moves.
        """
        piece_function = self.base_move.get_piece_type_function(rank_i_old, file_i_old, board)
        if piece_function is not None:
            moves = piece_function(rank_i_old, file_i_old, board)
            moves = moves + self.castle.get_castle_moves(rank_i_old, file_i_old, board, castle_avail)
            moves = moves + self.enpassant.get_enpassant_moves(rank_i_old, file_i_old, board, enpassant)
            if moves is not None:
                return self.filter_moves(rank_i_old, file_i_old, moves, board)
            print("WARNING: Moves does not exist.")
        else:
            print("WARNING: Piece function does not exist.")
        return []
    
    def update_valid_moves(self, rank_i_old: int, file_i_old: int, board: list, castle_avail: str, enpassant: str) -> "ChessMoves":
        """Calculates new valid moves and updates valid_moves member.

            Returns: Self for chaining
        """
        self._valid_moves = self.get_valid_moves(rank_i_old, file_i_old, board, castle_avail, enpassant)
        return self
    
    def clear_valid_moves(self) -> "ChessMoves":
        """Empties the valid moves stored in buffer.

            Returns: Self for chaining
        """
        self._valid_moves = []
        return self
    
    def valid_moves_is_empty(self) -> bool:
        """Determines if there are valid moves in the valid_moves buffer.

            Returns: True if valid_moves is empty, false if otherwise
        """
        if len(self._valid_moves) > 0:
            return False
        return True
    
    def valid_moves_has_move(self, move: tuple) -> bool:
        """Determines if the passed move exists in valid_moves.

            Returns: True if exists, false if otherwise
        """
        if self._valid_moves.count(move) > 0:
            return True
        return False
    
    def get_valid_moves_list(self) -> list:
        """Get the list of valid moves.

            Returns: List of all valid moves.
        """
        return self._valid_moves

    def get_move_str(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list, castled: bool, enpassant: bool) -> str:
        """Get the move string of the passed move (rank_i_old, file_i_old) -> (rank_i_new, file_i_new).

            Returns: Move String.
        """
        if castled:
            return self.castle.get_castle_str(file_i_old, file_i_new)

        board_position_old = rank_i_old * self.board.files + file_i_old
        board_position_new = rank_i_new * self.board.files + file_i_new

        #Get the pieces that are moving and the captured piece
        moving_piece = board[board_position_old]
        destination_piece = board[board_position_new]

        #Determine if a capture happened
        capture_string = ""
        if destination_piece != 0 or enpassant:
            capture_string = "x"

        #Get the destination rank and file
        destination_rank_str: str = str(self.board.ranks - rank_i_new)
        destination_file_str: str = self.utils.get_file_from_number(file_i_new)
        moving_piece_file_str: str = ''
        moving_piece_str: str = self.utils.get_str_from_piece_type(moving_piece, self.board.piece_numbers, True)

        #Show file from for certain cases
        if moving_piece_str == 'P' and capture_string == 'x':
            moving_piece_file_str = self.utils.get_file_from_number(file_i_old)

        #Remove the P if it was a Pawn
        if moving_piece_str == 'P':
            moving_piece_str = ''

        #Return the entire Move string
        return moving_piece_file_str + moving_piece_str + capture_string + destination_file_str + destination_rank_str

    def move(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list, whites_turn: bool, castle_avail: str, enpassant: str, full_move: int) -> dict | None:
        """ Moves the piece on the passed board.

            Gets the new Move string.
            Updates turn.
            Updates castle availability.
            Updates En Passant Availability
            Updates half moves.
            Updates full moves.
            Generates new FEN String.

            Returns: dict[  "board"   "move_str"    "move_tuple"    "whites_turn"     "fen_string"   "castle_avail"    "en_passant"    "half_move"    "full_move"    ] or None if no move.
        """
        board_position_old = rank_i_old * self.board.files + file_i_old
        board_position_new = rank_i_new * self.board.files + file_i_new

        if board_position_old < len(board) and board_position_new < len(board):
            
            #Update Piece on board
            new_board = board.copy()
            new_board[board_position_new] = new_board[board_position_old]
            new_board[board_position_old] = 0

            #Castle
            castle_bool = False
            if self.castle.move_is_castle(rank_i_old, file_i_old, rank_i_new, file_i_new, board):
                self.castle.castle_rook(rank_i_old, file_i_old, rank_i_new, file_i_new, new_board)
                castled = True

            #Enpassant
            enpassant_bool = False
            if self.enpassant.move_is_enpassant(rank_i_old, file_i_old, rank_i_new, file_i_new, board, enpassant):
                self.enpassant.take_pawn(rank_i_old, file_i_old, rank_i_new, file_i_new, new_board)
                enpassant_bool = True

            #Update Turn
            white_turn = False if whites_turn else True

            #Get Castle Availability
            castle = self.castle.update_avail(rank_i_old, file_i_old, board, castle_avail)
            if castle == "":
                castle = "-"

            #Get En Passant Availability
            en_passant = self.enpassant.get_enpassant_str(rank_i_old, file_i_old, rank_i_new, file_i_new, board)

            #Get Half Move
            half_move = 0

            #Get Full Move
            full_move_new = int(full_move)
            if whites_turn is True:
                full_move_new += 1

            #Get Move String
            new_move_str = self.get_move_str(rank_i_old, file_i_old, rank_i_new, file_i_new, board, castle_bool, enpassant_bool)

            #Get New FEN String
            new_fen = self.utils.convert_board_to_fen(new_board,
                                                        white_turn,
                                                        castle,
                                                        en_passant,
                                                        half_move,
                                                        full_move_new,
                                                        self.board.files,
                                                        self.board.ranks, 
                                                        self.board.piece_numbers)
            
            print(f"New Move: {new_move_str}")
            print(f"New FEN: {new_fen}")
            return {
                "board": new_board,
                "move_str": new_move_str,
                "move_tuple": (rank_i_old, file_i_old, rank_i_new, file_i_new),
                "whites_turn": white_turn,
                "fen_string": new_fen,
                "castle_avail": castle,
                "en_passant": en_passant,
                "half_move": half_move,
                "full_move": full_move_new
            }

        return None