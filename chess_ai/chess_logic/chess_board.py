
from .chess_piece import ChessPiece
from .chess_utils import ChessUtils
from .chess_move import ChessMove

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


        #Game Status
        self.ranks = ranks
        self.files = files
        self.whites_turn = whites_turn
        self.check_status = check_status
        self.en_passant = en_passant
        self.castle_avail = castle_avail
        self.half_move = half_move
        self.max_half_moves = max_half_moves
        self.full_move = full_move

        #Positions for optimized searching
        self.value_board = [0] * ranks * files
        self.piece_board = [None] * ranks * files
        self.white_positions = []
        self.black_positions = []
        self.white_moves = []
        self.black_moves = []
        self.white_attacks = []
        self.black_attacks = []
        self.king_positions = [None, None]
        self.in_check = False
        self.checking_pieces = []
        self.last_move_castle = False
        self.last_move_en_passant = False

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

    def copy(self) -> "ChessBoard":
        new_board = ChessBoard(
            self.utils.piece_values, 
            self.utils.piece_scores,
            self.ranks,
            self.files,
            self.whites_turn,
            self.check_status,
            self.en_passant,
            self.castle_avail,
            self.half_move,
            self.max_half_moves,
            self.full_move
        )
        new_board.value_board = self.value_board
        new_board.piece_board = self.piece_board
        new_board.white_positions = self.white_positions
        new_board.black_positions = self.black_positions
        new_board.white_moves = self.white_moves
        new_board.black_moves = self.black_moves
        new_board.white_attacks = self.white_attacks
        new_board.black_attacks = self.black_attacks
        new_board.king_positions = self.king_positions
        new_board.in_check = self.in_check
        new_board.checking_pieces = self.checking_pieces
        new_board.last_move_castle = self.last_move_castle
        new_board.last_move_en_passant = self.last_move_en_passant
        return new_board
    
    def _move_new_board(self, new_move: ChessMove) -> "ChessBoard":
        """Creates a new board and performs a move on that board. Does not edit current board.

            Returns: new board that has been edited
        """
        #Get new copy of board
        new_board = self.copy()

        #Perform Move
        old_pos = new_move.piece.position[0] * self.files +  new_move.piece.position[1]
        new_pos = new_move.new_position[0] * self.files +  new_move.new_position[1]
        new_board.piece_board[new_pos] = new_board.piece_board[old_pos]
        new_board.piece_board[old_pos] = 0

        #Update Data Trackers
        if new_board.whites_turn:
            new_board.white_positions.remove((new_move.piece.position[0], new_move.piece.position[1]))
            new_board.white_positions.append((new_move.new_position[0], new_move.new_position[1]))
            if new_board.black_positions.count((new_move.new_position[0], new_move.new_position[1])) > 0:
                new_board.black_positions.remove((new_move.new_position[0], new_move.new_position[1]))
            if new_move.piece.type == "K":
                new_board.king_positions[0] = new_move.new_position
        else:
            new_board.black_positions.remove((new_move.piece.position[0], new_move.piece.position[1]))     
            new_board.black_positions.append((new_move.new_position[0], new_move.new_position[1]))       
            if new_board.white_positions.count((new_move.new_position[0], new_move.new_position[1])) > 0:
                new_board.white_positions.remove((new_move.new_position[0], new_move.new_position[1]))
            if new_move.piece.type == "K":
                new_board.king_positions[1] = new_move.new_position

        #See if move is castle
        if new_move.castle:
            old_pos = new_move.castle_rook_move.piece.position[0] * self.files +  new_move.castle_rook_move.piece.position[1]
            new_pos = new_move.castle_rook_move.new_position[0] * self.files +  new_move.castle_rook_move.new_position[1]
            new_board.piece_board[new_pos] = new_board.piece_board[old_pos]
            new_board.piece_board[old_pos] = 0
            
        #See if move is enpassant
        elif new_move.en_passant:
            pos = new_move.en_passant_pawn.position[0] * self.files +  new_move.en_passant_pawn.position[1]
            new_board.piece_board[pos] = 0
            if new_board.whites_turn:
                new_board.black_positions.remove((new_move.en_passant_pawn.position[0], new_move.en_passant_pawn.position[1]))
            else:
                new_board.white_positions.remove((new_move.en_passant_pawn.position[0], new_move.en_passant_pawn.position[1]))

        #Update Turn
        new_board.whites_turn = True if new_board.whites_turn else new_board.whites_turn
        return new_board

    def check_move_for_check(self, new_move: ChessMove) -> bool:
        """Creates a new board to simulate new move to see if other team is able to check.

            Returns: True if other team is able to check our king.
        """
        new_board = self._move_new_board(new_move)
        if new_board.whites_turn:
            for r, f in new_board.black_positions:
                piece: ChessPiece = new_board.piece_board[r * new_board.files + f]
                if piece.get_piece_check(new_board):
                    return True
        else:
            for r, f in new_board.white_positions:
                piece: ChessPiece = new_board.piece_board[r * new_board.files + f]
                if piece.get_piece_check(new_board):
                    return True
        return False
    
    def calc_check_status(self) -> "ChessBoard":
        """Calculates the check status of the current board. The move list must be up to date.

            Returns: Self for chaining.
        """
        if self.whites_turn:
            #Get in check
            move: ChessMove
            in_check = False
            for move in self.black_attacks:
                if move.new_position == self.king_positions[0]:
                    in_check = True
                    break
            #Calc check status 0 = Stale, 1 = Check, 2 = Checkmate
            if in_check:
                if len(self.white_moves) == 0:
                    self.check_status = -2
                else:
                    self.check_status = -1
            else:
                if len(self.white_moves) == 0:
                    self.check_status = 0
                else:
                    self.check_status = None
        else:
            #Get in check
            move: ChessMove
            in_check = False
            for move in self.white_attacks:
                if move.new_position == self.king_positions[1]:
                    in_check = True
                    break
            #Calc check status 0 = Stale, 1 = Check, 2 = Checkmate
            if in_check:
                if len(self.black_moves) == 0:
                    self.check_status = -2
                else:
                    self.check_status = -1
            else:
                if len(self.black_moves) == 0:
                    self.check_status = 0
                else:
                    self.check_status = None
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
    


    