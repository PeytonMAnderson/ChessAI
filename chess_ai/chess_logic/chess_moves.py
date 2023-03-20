
from .chess_utils import ChessUtils
from .chess_board import ChessBoard
from .chess_base_moves import ChessBaseMoves
from .chess_check import ChessCheck
from .chess_castle import ChessCastle
from .chess_enpassant import ChessEnpassant
from .chess_promotion import ChessPromotion
from .chess_score import ChessScore

class ChessMoves:
    def __init__(self, 
                utils: ChessUtils, 
                board: ChessBoard, 
                base_move: ChessBaseMoves, 
                check: ChessCheck, 
                castle: ChessCastle, 
                enpassant: ChessEnpassant, 
                promote: ChessPromotion, 
                score: ChessScore,
        *args, **kwargs) -> None:
        self.utils = utils
        self.board = board
        self.base_move = base_move
        self.check = check
        self.castle = castle
        self.enpassant = enpassant
        self.promote = promote
        self.score = score
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
            print(f"WARNING: Piece function does not exist. {rank_i_old, file_i_old}")
        return []
    
    def get_all_valid_moves(self, board: list, castle_avail: str, enpassant: str, is_white: bool) -> list:
        all_valid_moves = []
        rank_i = 0
        file_i = 0
        while rank_i < self.board.ranks:
            file_i = 0
            while file_i < self.board.files:
                piece_value = board[rank_i * self.board.files + file_i]
                if piece_value != 0 and self.utils.get_is_white_from_piece_number(piece_value, self.board.piece_numbers) == is_white:
                    new_moves = self.get_valid_moves(rank_i, file_i, board, castle_avail, enpassant)
                    for r, f in new_moves:
                        all_valid_moves.append((rank_i, file_i, r, f))
                file_i += 1
            rank_i += 1
        return all_valid_moves

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

    def get_move_str(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list, castled: bool, enpassant: bool, captured: bool, check_status: int) -> str:
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
        if captured != 0 or enpassant:
            print(f"{destination_piece} -> {enpassant}")
            capture_string = "x"

        #Get the destination rank and file
        destination_rank_str: str = self.utils.get_rank_from_number(rank_i_new, self.board.ranks)
        destination_file_str: str = self.utils.get_file_from_number(file_i_new)
        moving_piece_file_str: str = ''
        moving_piece_str: str = self.utils.get_str_from_piece_type(moving_piece, self.board.piece_numbers, True)

        #Show file from for certain cases
        if moving_piece_str == 'P' and capture_string == 'x':
            new_str = self.utils.get_file_from_number(file_i_old)
            moving_piece_file_str = new_str if new_str is not None else ''

        #Remove the P if it was a Pawn
        if moving_piece_str == 'P' or moving_piece_str is None:
            moving_piece_str = ''

        #Return the entire Move string
        return moving_piece_file_str + moving_piece_str + capture_string + destination_file_str + destination_rank_str

    def simulate_move(self, rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list, castle_avail: str, en_passant: str) -> list:
        """Simulates an advanced move and returns the board with that move. Accounts for promotions, castling, en passant, etc. 

        Args:
            rank_i_old (int): rank of old position for piece
            file_i_old (int): file of old position for piece
            rank_i_new (int): rank of new position for piece
            file_i_new (int): file of new position for piece
            board (list): board that will be modified
            castle_avail (str): string of castling availability (KQkq)
            en_passant (str): string of en passant availability (e3)

        Returns:
            list: [ new_board, castle_str, en_passant_str, castle_bool, en_passant_bool]
        """
        board_position_old = rank_i_old * self.board.files + file_i_old
        board_position_new = rank_i_new * self.board.files + file_i_new
        if board_position_old < len(board) and board_position_new < len(board):

            #Captured Piece
            captured = False
            if new_board[board_position_new] != 0:
                captured = True

            #Update Piece on board
            new_board = board.copy()
            new_board[board_position_new] = new_board[board_position_old]
            new_board[board_position_old] = 0

            #Promote
            if self.promote.move_can_promote(rank_i_old, file_i_old, rank_i_new, file_i_new, board):
                piece_value = self.utils.get_piece_number_on_board(rank_i_old, file_i_old, board, self.board.files)
                is_white = self.utils.get_is_white_from_piece_number(piece_value, self.board.piece_numbers)
                queen = 'Q' if is_white else 'q'
                new_board[board_position_new] = self.utils.get_piece_number_from_str(queen, self.board.piece_numbers)

            #Castle
            castle_bool = False
            if self.castle.move_is_castle(rank_i_old, file_i_old, rank_i_new, file_i_new, board):
                self.castle.castle_rook(rank_i_old, file_i_old, rank_i_new, file_i_new, new_board)
                castle_bool = True

            #Enpassant
            en_passant_bool = False
            if self.enpassant.move_is_enpassant(rank_i_old, file_i_old, rank_i_new, file_i_new, board, en_passant):
                self.enpassant.take_pawn(rank_i_old, file_i_old, rank_i_new, file_i_new, new_board)
                en_passant_bool = True

            #Get Castle Availability
            castle_str = self.castle.update_avail(rank_i_old, file_i_old, board, castle_avail)
            if castle_str == "":
                castle_str = "-"

            #Get En Passant Availability
            en_passant_str = self.enpassant.get_enpassant_str(rank_i_old, file_i_old, rank_i_new, file_i_new, board)

            return new_board, castle_str, en_passant_str, castle_bool, en_passant_bool

        print("WARNING: Position is out of bounds.")
        return board, castle_avail, en_passant, False, False, captured

    def move(self, 
             rank_i_old: int, 
             file_i_old: int, 
             rank_i_new: int, 
             file_i_new: int, 
             board: list, 
             whites_turn: bool, 
             castle_avail: str, 
             en_passant: str, 
             half_move: int, 
             full_move: int) -> dict | None:
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
        #Get Half Move
        half_move_new = int(half_move)
        if board[rank_i_new * self.board.files + file_i_new] != 0:
            half_move_new = 0
        else:
            half_move_new += 1

        #Update Piece on board
        new_board, castle_str, en_passant_str, castle_bool, en_passant_bool, captured = self.simulate_move(rank_i_old, file_i_old, rank_i_new, file_i_new, board, castle_avail, en_passant)

        #Get Full Move
        full_move_new = int(full_move)
        if whites_turn is True:
            full_move_new += 1

        #Get New Color
        white_turn = False if whites_turn else True

        #Get New FEN String
        new_fen = self.utils.convert_board_to_fen(new_board,
                                                    white_turn,
                                                    castle_str,
                                                    en_passant_str,
                                                    half_move_new,
                                                    full_move_new,
                                                    self.board.files,
                                                    self.board.ranks, 
                                                    self.board.piece_numbers)
    
        return {
            "board": new_board,
            "move_tuple": (rank_i_old, file_i_old, rank_i_new, file_i_new),
            "whites_turn": white_turn,
            "fen_string": new_fen,
            "castle_avail": castle_str,
            "en_passant": en_passant_str,
            "half_move": half_move_new,
            "full_move": full_move_new,
            "castle_bool": castle_bool, 
            "en_passant_bool": en_passant_bool,
            "captured": captured
        }
    
    def calc_best_move(self, board: list, is_white: bool, castle_avail: str, en_passant:str) -> tuple:
        #Get Variables
        best_score = None
        best_color_score = None
        best_move = None
        branches = 0

        #Loop through their moves to see what they would choose
        moves_list = self.get_all_valid_moves(board, castle_avail, en_passant, is_white)
        for ro, fo, rf, ff in moves_list:
            #Get their new board for their moves
            new_board, _, _, _, _ = self.simulate_move( ro, fo, rf, ff, board, castle_avail, en_passant)
            new_score = self.score.calc_game_score(new_board, not is_white)

            #Calculate their score
            color_score = new_score if is_white else 0 - new_score

            #If their new score is their best one yet, save their values
            if best_color_score is None or color_score > best_color_score:
                best_color_score = color_score
                best_score = new_score 
                best_move = (ro, fo, rf, ff)
            branches += 1
        return best_score, best_move, branches