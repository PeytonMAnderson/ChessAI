from copy import deepcopy

from .chess_piece import ChessPiece
from .chess_utils import ChessUtils
from .chess_move import ChessMove

class ChessBoard:
    def __init__(self,
        utils: ChessUtils,
        ranks: int = 8,
        files: int = 8,
        whites_turn: bool = True,
        check_status: int | None = None,
        en_passant: str = "-",
        castle_avail: str = "KQkq",
        half_move: int = 0,
        full_move: int = 0,
        piece_board: list = [],
        white_positions: list = [],
        black_positions: list = [],
        white_moves: list = [],
        black_moves: list =  [],
        king_positions: list = [None, None],
        last_move_castle: bool = False,
        last_move_en_passant: bool = False,
    *args, **kwargs) -> None:
        """ A chess board that can be populated with pieces and updated.
        """
        #Game Status
        self.ranks = ranks
        self.files = files
        self.whites_turn = whites_turn
        self.check_status = check_status
        self.en_passant = en_passant
        self.castle_avail = castle_avail
        self.half_move = half_move
        self.full_move = full_move
        self.utils = utils

        #Positions for optimized searching
        if len(piece_board) == 0:
            self.piece_board = [None] * ranks * files
        else:
            self.piece_board = piece_board
        self.white_positions = white_positions  
        self.black_positions = black_positions  
        self.white_moves = white_moves
        self.black_moves = black_moves
        self.king_positions = king_positions
        self.last_move_castle = last_move_castle
        self.last_move_en_passant = last_move_en_passant

    def fen_to_board(self, fen_str: str) -> "ChessBoard":
        """Updates the entire board from the FEN string.

            Returns: Self for chaining.
        """
        #Reset Board:
        self.piece_board = [None] * self.ranks * self.files
        self.white_positions = []
        self.black_positions = []
        self.white_moves = []
        self.black_moves = []
        self.king_positions = [None, None]
        
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
                    if len(self.piece_board) > loc:
                        piece_value = self.utils._calc_piece_value(piece_str=piece)
                        piece_type, piece_color = self.utils._calc_piece_type_color(piece_str=piece)
                        self.piece_board[loc] = ChessPiece(piece_value, piece_type, piece_color, (rank_index, file_index))
                        if piece_color:
                            self.white_positions.append((rank_index, file_index))
                            if piece_type == "K":
                                self.king_positions[0] = (rank_index, file_index)
                        else:
                            self.black_positions.append((rank_index, file_index))
                            if piece_type == "K":
                                self.king_positions[1] = (rank_index, file_index)

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
        
        #Update
        self._calc_new_team_moves()
        self.calc_check_status()

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
                if isinstance(piece, ChessPiece):
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

    def _simulate_move(self, new_move: ChessMove) -> tuple[list, list, list, list, bool]:
        new_piece_board = self.piece_board.copy()
        other_teams_positions = self.white_positions.copy() if not self.whites_turn else self.black_positions.copy()
        new_king_positions = self.king_positions.copy()

        #Perform Move
        old_pos = new_move.piece.position[0] * self.files +  new_move.piece.position[1]
        new_pos = new_move.new_position[0] * self.files +  new_move.new_position[1]
        new_piece_board[new_pos] = new_piece_board[old_pos]
        new_piece_board[old_pos] = None

        #Update Data Trackers
        if self.whites_turn:
            if other_teams_positions.count((new_move.new_position[0], new_move.new_position[1])) > 0:
                other_teams_positions.remove((new_move.new_position[0], new_move.new_position[1]))
            if new_move.piece.type == "K":
                new_king_positions[0] = new_move.new_position
        else:     
            if other_teams_positions.count((new_move.new_position[0], new_move.new_position[1])) > 0:
                other_teams_positions.remove((new_move.new_position[0], new_move.new_position[1]))
            if new_move.piece.type == "K":
                new_king_positions[1] = new_move.new_position

        #See if move is castle
        if new_move.castle:
            old_pos = new_move.castle_rook_move.piece.position[0] * self.files +  new_move.castle_rook_move.piece.position[1]
            new_pos = new_move.castle_rook_move.new_position[0] * self.files +  new_move.castle_rook_move.new_position[1]
            new_piece_board[new_pos] = new_piece_board[old_pos]
            new_piece_board[old_pos] = None
            
        #See if move is enpassant
        elif new_move.en_passant:
            pos = new_move.en_passant_pawn.position[0] * self.files +  new_move.en_passant_pawn.position[1]
            new_piece_board[pos] = None
            if self.whites_turn:
                other_teams_positions.remove((new_move.en_passant_pawn.position[0], new_move.en_passant_pawn.position[1]))
            else:
                other_teams_positions.remove((new_move.en_passant_pawn.position[0], new_move.en_passant_pawn.position[1]))

        #Update Turn
        return new_piece_board, other_teams_positions, new_king_positions
        
    
    def _new_move(self, new_move: ChessMove) -> "ChessBoard":
        """Updates the board with the new move. Does not update check status, castling string etc.

            Returns: Self for chaining
        """
        #Perform Move
        old_pos = new_move.piece.position[0] * self.files +  new_move.piece.position[1]
        new_pos = new_move.new_position[0] * self.files +  new_move.new_position[1]
        captured = True if self.piece_board[new_pos] is not None else False
        self.piece_board[new_pos] = self.piece_board[old_pos]
        self.piece_board[old_pos] = None

        #Update Data Trackers
        if self.whites_turn:
            self.white_positions.remove((new_move.piece.position[0], new_move.piece.position[1]))
            self.white_positions.append((new_move.new_position[0], new_move.new_position[1]))
            if self.black_positions.count((new_move.new_position[0], new_move.new_position[1])) > 0:
                self.black_positions.remove((new_move.new_position[0], new_move.new_position[1]))
            if new_move.piece.type == "K":
                self.king_positions[0] = new_move.new_position
        else:
            self.black_positions.remove((new_move.piece.position[0], new_move.piece.position[1]))     
            self.black_positions.append((new_move.new_position[0], new_move.new_position[1]))       
            if self.white_positions.count((new_move.new_position[0], new_move.new_position[1])) > 0:
                self.white_positions.remove((new_move.new_position[0], new_move.new_position[1]))
            if new_move.piece.type == "K":
                self.king_positions[1] = new_move.new_position

        #See if move is castle
        self.last_move_castle = False
        self.last_move_en_passant = False
        if new_move.castle:
            old_rook_pos = new_move.castle_rook_move.piece.position[0] * self.files +  new_move.castle_rook_move.piece.position[1]
            new_rook_pos = new_move.castle_rook_move.new_position[0] * self.files +  new_move.castle_rook_move.new_position[1]
            self.piece_board[new_rook_pos] = self.piece_board[old_rook_pos]
            self.piece_board[old_rook_pos] = None
            self.last_move_castle = True
            if self.whites_turn:
                self.white_positions.remove((new_move.castle_rook_move.piece.position[0], new_move.castle_rook_move.piece.position[1]))
                self.white_positions.append((new_move.castle_rook_move.new_position[0], new_move.castle_rook_move.new_position[1]))
            else:
                self.black_positions.remove((new_move.castle_rook_move.piece.position[0], new_move.castle_rook_move.piece.position[1]))
                self.black_positions.append((new_move.castle_rook_move.new_position[0], new_move.castle_rook_move.new_position[1]))
            self.piece_board[new_rook_pos].position = new_move.castle_rook_move.new_position
            
        #See if move is enpassant
        elif new_move.en_passant:
            pos = new_move.en_passant_pawn.position[0] * self.files +  new_move.en_passant_pawn.position[1]
            self.piece_board[pos] = None
            if self.whites_turn:
                self.black_positions.remove((new_move.en_passant_pawn.position[0], new_move.en_passant_pawn.position[1]))
            else:
                self.white_positions.remove((new_move.en_passant_pawn.position[0], new_move.en_passant_pawn.position[1]))
            self.last_move_en_passant = True

        #Pawn Promotion
        if new_move.promotion:
            self.piece_board[new_pos].type = new_move.promotion_type
            self.piece_board[new_pos].set_type_functions()

        #Update Piece
        self.piece_board[new_pos].position = new_move.new_position

        #Update half and full move
        self.half_move = 0 if captured else self.half_move + 1
        self.full_move = self.full_move + 1 if self.whites_turn else self.full_move 

        #Update Turn
        self.whites_turn = False if self.whites_turn else True
        return self

    def check_move_for_check(self, new_move: ChessMove) -> bool:
        """Creates a new board to simulate new move to see if other team is able to check.

            Returns: True if other team is able to check our king.
        """
        new_piece_board, other_teams_positions, new_king_positions = self._simulate_move(new_move)
        for r, f in other_teams_positions:
            piece: ChessPiece = new_piece_board[r * self.files + f]
            if piece.get_piece_check(new_piece_board, new_king_positions, (self.ranks, self.files)):
                return True
        return False
    
    def calc_check_status(self) -> "ChessBoard":
        """Calculates the check status of the current board. The move list must be up to date.

            Returns: Self for chaining.
        """
        if self.whites_turn:
            #Get in check
            in_check = False
            for r, f in self.black_positions:
                piece: ChessPiece = self.piece_board[r * self.files + f]
                if piece.get_piece_check(self.piece_board, self.king_positions, (self.ranks, self.files)):
                    in_check = True
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
            in_check = False
            for r, f in self.white_positions:
                piece: ChessPiece = self.piece_board[r * self.files + f]
                if piece.get_piece_check(self.piece_board, self.king_positions, (self.ranks, self.files)):
                    in_check = True
            #Calc check status 0 = Stale, 1 = Check, 2 = Checkmate
            if in_check:
                if len(self.black_moves) == 0:
                    self.check_status = 2
                else:
                    self.check_status = 1
            else:
                if len(self.black_moves) == 0:
                    self.check_status = 0
                else:
                    self.check_status = None
        return self
    
    def _calc_new_team_moves(self) -> "ChessBoard":
        if self.whites_turn:
            new_moves = []
            for r, f in self.white_positions:
                white_piece: ChessPiece = self.piece_board[r * self.files + f]
                new_moves = new_moves + white_piece.calc_moves_attacks(self).moves
            self.white_moves = new_moves
            self.black_moves = []
        else:
            new_moves = []
            for r, f in self.black_positions:
                black_piece: ChessPiece = self.piece_board[r * self.files + f]
                new_moves = new_moves + black_piece.calc_moves_attacks(self).moves
            self.black_moves = new_moves
            self.white_moves = []
        return self

    def move_piece(self, new_move: ChessMove, create_new_board: bool = False) -> "ChessBoard":
        #Get new copy of board
        new_board = deepcopy(self) if create_new_board else self

        #Update Castle Str
        if new_move.piece.type == "K":
            if new_board.whites_turn:
                new_board.castle_avail = new_board.castle_avail.replace('K', '').replace('Q','')
            else:
                new_board.castle_avail = new_board.castle_avail.replace('k', '').replace('q','')
        elif new_move.piece.type == "R":
            if new_board.whites_turn:
                if new_move.piece.position[1] == 0:
                    new_board.castle_avail = new_board.castle_avail.replace('Q', '')
                elif new_move.piece.position[1] == new_board.files-1:
                    new_board.castle_avail = new_board.castle_avail.replace('K', '')
            else:
                if new_move.piece.position[1] == 0:
                    new_board.castle_avail = new_board.castle_avail.replace('q', '')
                elif new_move.piece.position[1] == new_board.files-1:
                    new_board.castle_avail = new_board.castle_avail.replace('k', '')
        new_board.castle_avail = '-' if new_board.castle_avail == '' else new_board.castle_avail
        
        #Update En passant str
        new_board.en_passant = "-"
        if new_move.piece.type == "P":
            if new_move.new_position[0] - new_move.piece.position[0] == 2:
                r = new_move.piece.position[0] + 1
                rank = new_board.utils.get_rank_from_number(r, new_board.ranks)
                file = new_board.utils.get_file_from_number(new_move.new_position[1])
                new_board.en_passant = file + rank
            elif new_move.new_position[0] - new_move.piece.position[0] == -2:
                r = new_move.piece.position[0] - 1
                rank = new_board.utils.get_rank_from_number(r, new_board.ranks)
                file = new_board.utils.get_file_from_number(new_move.new_position[1])
                new_board.en_passant = file + rank

        #Execute Move
        new_board._new_move(new_move)

        #Update Current Teams Moves
        new_board._calc_new_team_moves()

        #Update Check Status
        new_board.calc_check_status()

        return new_board
    
    


    