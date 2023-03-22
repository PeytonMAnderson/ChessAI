
from .chess_piece import ChessPiece
from .chess_utils import ChessUtils

class ChessBoard:
    def __init__(self,
        piece_values: dict,
        piece_scores: dict,
        ranks: int = 8,
        files: int = 8,
        whites_turn: bool = True,
        check_status: int | None = None,
        en_passant: str = "-",
        castle_avail: str = "KQkq",
        half_move: int = 0,
        max_half_moves: int = 50,
        full_move: int = 0,
    *args, **kwargs) -> None:
        """ A Empty chess board that can be populated with pieces and updated.
        """
        #Board
        self.ranks = ranks
        self.files = files
        self.value_board = [0] * ranks * files
        self.piece_board = [None] * ranks * files

        #Game Status
        self.whites_turn = whites_turn
        self.check_status = check_status
        self.en_passant = en_passant
        self.castle_avail = castle_avail
        self.half_move = half_move
        self.max_half_moves = max_half_moves
        self.full_move = full_move
        self.last_move_castle = False
        self.last_move_en_passant = False

        #Positions for optimized searching
        self.white_positions = []
        self.black_positions = []
        self.white_moves = []
        self.black_moves = []
        self.king_positions = [None, None]
        self.in_check = False
        self.checking_pieces = []

        #Helper Functions
        self.utils = ChessUtils(piece_values, piece_scores)

    def fen_to_board(self, fen_str: str) -> "ChessBoard":
        """Updates the entire board from the FEN string.

            Returns: Self for chaining.
        """
        #Reset Board:
        self.value_board = [0] * self.ranks * self.files
        self.piece_board = [None] * self.ranks * self.files
        
        #Get the piece positions from the fen string
        split_string = fen_str.split(" ")
        piece_positions = split_string[0]
        turn = split_string[1] if len(split_string) >= 2 else None
        castle_avail = split_string[2] if len(split_string) >= 3 else None
        enpassant = split_string[3] if len(split_string) >= 4 else None
        half_move = split_string[4] if len(split_string) >= 5 else None
        full_move = split_string[5] if len(split_string) >= 6 else None

        #Go through the ranks
        piece_ranks = piece_positions.split("/")
        rank_index = 0
        for rank in piece_ranks:

            #Go through the files
            file_index = 0
            string_index = 0
            while file_index < self.files and string_index < len(rank):
                piece = rank[string_index]
                if piece.isdigit() is False:
                    loc = rank_index * self.files + file_index
                    if len(self.value_board) > loc:
                        piece_value = self.utils._calc_piece_value(piece_str=piece)
                        piece_type, piece_color = self.utils._calc_piece_type_color(piece_str=piece)
                        self.value_board[loc] = piece_value
                        self.piece_board[loc] = ChessPiece(piece_value, piece_type, piece_color, (rank_index, file_index))
                    file_index += 1
                    string_index += 1
                else:
                    file_index += int(piece)
                    string_index += 1
            rank_index += 1

        #Game State
        self.whites_turn = True if turn is None or turn == 'w' else False
        self.castle_avail = castle_avail
        self.en_passant = enpassant
        self.half_move = int(half_move)
        self.full_move = int(full_move)
        
        #Update Check status
        #----

        #Return self
        return self
    
    def board_to_fen(self) -> str:
        """Generates a FEN string from the current board.

            Returns: FEN string.
        """
        rank_index = 0
        file_index = 0

        rank_str = ""
        #Go Through ranks
        while rank_index < self.ranks:

            #Go Through Files
            file_str_total = ""
            file_str_prev = ''
            file_index = 0
            while file_index < self.files:

                #Get piece from board
                loc = rank_index * self.files + file_index
                piece: ChessPiece = self.piece_board[loc]

                #If location is a piece
                if piece is not None:
                    s = self.utils._calc_piece_str(piece_type=piece.type, is_white=piece.is_white)
                    file_str_prev = s
                    file_str_total = file_str_total + s
                else:
                    #If Previous str was also a digit, increment instead of adding new
                    if file_str_prev.isdigit():
                        prev_digit = int(file_str_prev)
                        file_str_total = file_str_total.removesuffix(file_str_prev)
                        file_str_prev = str(prev_digit + 1)
                        file_str_total = file_str_total + str(prev_digit + 1)
                    
                    #New Space, add 1 as beginning digit
                    else:
                        file_str_prev = "1"
                        file_str_total = file_str_total + "1"
                #Increment File
                file_index += 1
            #Add Rank to rank String
            if len(rank_str) > 0:
                rank_str = rank_str + "/" + file_str_total
            else:
                rank_str = file_str_total
            #Increment Rank
            rank_index += 1
        
        #Add Active color:
        color_str = "w" if self.whites_turn else "b"
        return rank_str + " " + color_str + " " + self.castle_avail + " " + self.en_passant + " " + str(self.half_move) + " " + str(self.full_move)
    
    def _move_piece_basic(self, rank_old: int, file_old: int, rank_new: int, file_new: int) -> "ChessBoard":
        old_loc = rank_old * self.files + file_old
        new_loc = rank_new * self.files + file_new
        self.value_board[new_loc] = self.value_board[old_loc]
        self.piece_board[new_loc] = self.piece_board[old_loc]
        self.value_board[old_loc] = 0
        self.piece_board[old_loc] = None
        return self
    
    def _update_others_moves(self) -> "ChessBoard":
        """If whites_turn, calculates the attacking moves of black. Else, moves of white.

            Returns: Self for chaining.
        """
        if not self.whites_turn:
            new_attacks = []
            for r, f in self.white_positions:
                new_pos = r * self.files + f
                piece: ChessPiece = self.piece_board[new_pos]
                piece.calc_positions(self)
                new_attacks = new_attacks + piece.attacks
            self.white_attacking_positions = new_attacks
        else:
            new_attacks = []
            for r, f in self.black_positions:
                new_pos = r * self.files + f
                piece: ChessPiece = self.piece_board[new_pos]
                piece.calc_positions(self)
                new_attacks = new_attacks + piece.attacks
            self.black_attacking_positions = new_attacks
    
    def _set_check(self) -> "ChessBoard":
        """Sets the in_check flag for the current board.

            Returns: self for chaining
        """
        if self.whites_turn:
            for ro, fo, rf, ff in self.black_attacking_positions:
                if (rf, ff) == self.king_positions[0]:
                    self.in_check = True
                    return self
            self.in_check = False
        else:
            for ro, fo, rf, ff in self.white_attacking_positions:
                if (rf, ff) == self.king_positions[1]:
                    self.in_check = True
                    return self
            self.in_check = False
        return self
    
    def _set_checking_pieces(self) -> "ChessBoard":
        self.checking_pieces = []
        positions = self.black_positions if self.whites_turn else self.white_positions
        king_position = self.king_positions[0] if self.whites_turn else self.king_positions[1]
        if self.whites_turn:
            for r, f in self.black_positions:
                pos = r * self.files + f
                piece: ChessPiece = self.piece_board[pos]
                for ro, fo, rf, ff in piece.attacks:
                    if self.king_positions[0] == (rf, ff):
                        self.checking_pieces.append(piece)
        else: 
            for r, f in self.white_positions:
                pos = r * self.files + f
                piece: ChessPiece = self.piece_board[pos]
                for ro, fo, rf, ff in piece.attacks:
                    if self.king_positions[1] == (rf, ff):
                        self.checking_pieces.append(piece)


    def _move_piece_update(self, rank_old: int, file_old: int, rank_new: int, file_new: int, moving_piece: ChessPiece) -> "ChessBoard":
        #Perform Move
        
        #Update Turn
        self.whites_turn = False if self.whites_turn else True

        #Update King position
        if moving_piece.type == "K":
            self.king_positions[0 if moving_piece.is_white else 1] = (rank_new, file_new)

        #Update attacking positions
        self._update_others_moves()._set_check()
        
        #Return self
        return self

    
    def move_piece(self, rank_old: int, file_old: int, rank_new: int, file_new: int) -> "ChessBoard":
        return self._move_piece_basic(rank_old, file_old, rank_new, file_new)
    
    def update_piece(self, rank_i: int, file_i: int, new_piece: ChessPiece = None) -> "ChessBoard":
        if new_piece is None:
            loc = rank_i * self.files + file_i
            self.value_board[loc] = 0
            self.piece_board[loc] = 0
        else:
            loc = rank_i * self.files + file_i
            self.value_board[loc] = new_piece.value
            self.piece_board[loc] = new_piece
    


    