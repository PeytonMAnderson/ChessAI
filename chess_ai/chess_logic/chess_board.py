from copy import deepcopy

from .chess_piece import ChessPiece
from .chess_utils import ChessUtils
from .chess_move import ChessMove

class ChessBoardState:
    def __init__(self, board_state: "ChessBoardState" = None, ranks: int = 8, files: int = 8, *args, **kwargs) -> None:
        if board_state is None:
            self.check_status = None
            self.en_passant = "-"
            self.castle_avail = "KQkq"
            self.half_move = 0
            self.full_move = 0
            self.whites_turn = True
            self.piece_board = [None] * ranks * files
            self.white_positions = []
            self.black_positions = []  
            self.white_moves = []
            self.black_moves = []
            self.king_positions = [None, None]
        else:
            self.check_status = board_state.check_status
            self.en_passant = board_state.en_passant
            self.castle_avail = board_state.castle_avail
            self.half_move = board_state.half_move
            self.full_move = board_state.full_move
            self.whites_turn = board_state.whites_turn
            self.piece_board = deepcopy(board_state.piece_board)
            self.white_positions = board_state.white_positions.copy()
            self.black_positions = board_state.black_positions.copy()
            self.white_moves = board_state.white_moves.copy()
            self.black_moves = board_state.black_moves.copy()
            self.king_positions = board_state.king_positions.copy()


class ChessBoard:
    def __init__(self,
        utils: ChessUtils,
        ranks: int = 8,
        files: int = 8,
        board_state: ChessBoardState = None,
        last_move_castle: bool = False,
        last_move_en_passant: bool = False,
    *args, **kwargs) -> None:
        """ A chess board that can be populated with pieces and updated.
        """
        #Game Status
        self.ranks = ranks
        self.files = files
        self.utils = utils
        self.last_move_castle = last_move_castle
        self.last_move_en_passant = last_move_en_passant
        self.state = ChessBoardState(board_state, ranks, files)

    def fen_to_board(self, fen_str: str) -> "ChessBoard":
        """Updates the entire board from the FEN string.

            Returns: Self for chaining.
        """
        #Reset Board:
        self.state.piece_board = [None] * self.ranks * self.files
        self.state.white_positions = []
        self.state.black_positions = []
        self.state.white_moves = []
        self.state.black_moves = []
        self.state.king_positions = [None, None]
        
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
                    if len(self.state.piece_board) > loc:
                        piece_value = self.utils._calc_piece_value(piece_str=piece)
                        piece_type, piece_color = self.utils._calc_piece_type_color(piece_str=piece)
                        self.state.piece_board[loc] = ChessPiece(piece_value, piece_type, piece_color, (rank_index, file_index))
                        if piece_color:
                            self.state.white_positions.append((rank_index, file_index))
                            if piece_type == "K":
                                self.state.king_positions[0] = (rank_index, file_index)
                        else:
                            self.state.black_positions.append((rank_index, file_index))
                            if piece_type == "K":
                                self.state.king_positions[1] = (rank_index, file_index)

                    file_index += 1
                    string_index += 1
                else:
                    file_index += int(piece)
                    string_index += 1
            rank_index += 1

        #Game State
        self.state.whites_turn = True if turn is None or turn == 'w' else False
        self.state.castle_avail = castle_avail
        self.state.en_passant = enpassant
        self.state.half_move = int(half_move)
        self.state.full_move = int(full_move)
        
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
                piece: ChessPiece = self.state.piece_board[loc]

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
        color_str = "w" if self.state.whites_turn else "b"
        return rank_str + " " + color_str + " " + self.state.castle_avail + " " + self.state.en_passant + " " + str(self.state.half_move) + " " + str(self.state.full_move)

    def _simulate_move(self, new_move: ChessMove, chess_board_state: ChessBoardState) -> tuple[list, list, list, list, bool]:
        new_piece_board = chess_board_state.piece_board.copy()
        other_teams_positions = chess_board_state.white_positions.copy() if not chess_board_state.whites_turn else chess_board_state.black_positions.copy()
        new_king_positions = chess_board_state.king_positions.copy()

        #Perform Move
        old_pos = new_move.piece.position[0] * self.files +  new_move.piece.position[1]
        new_pos = new_move.new_position[0] * self.files +  new_move.new_position[1]
        new_piece_board[new_pos] = new_piece_board[old_pos]
        new_piece_board[old_pos] = None

        #Update Data Trackers
        if chess_board_state.whites_turn:
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
            if chess_board_state.whites_turn:
                other_teams_positions.remove((new_move.en_passant_pawn.position[0], new_move.en_passant_pawn.position[1]))
            else:
                other_teams_positions.remove((new_move.en_passant_pawn.position[0], new_move.en_passant_pawn.position[1]))

        #Update Turn
        return new_piece_board, other_teams_positions, new_king_positions
        
    
    def _new_move(self, new_move: ChessMove,  chess_board_state: ChessBoardState, update_state_only: bool = False) -> "ChessBoardState":
        """Updates the board with the new move. Does not update check status, castling string etc.

            Returns: Self for chaining
        """
        #Perform Move
        old_pos = new_move.piece.position[0] * self.files +  new_move.piece.position[1]
        new_pos = new_move.new_position[0] * self.files +  new_move.new_position[1]
        captured = True if chess_board_state.piece_board[new_pos] is not None else False
        chess_board_state.piece_board[new_pos] = chess_board_state.piece_board[old_pos]
        chess_board_state.piece_board[old_pos] = None

        #Update Data Trackers
        if chess_board_state.whites_turn:
            chess_board_state.white_positions.remove((new_move.piece.position[0], new_move.piece.position[1]))
            chess_board_state.white_positions.append((new_move.new_position[0], new_move.new_position[1]))
            if chess_board_state.black_positions.count((new_move.new_position[0], new_move.new_position[1])) > 0:
                chess_board_state.black_positions.remove((new_move.new_position[0], new_move.new_position[1]))
            if new_move.piece.type == "K":
                chess_board_state.king_positions[0] = new_move.new_position
        else:
            chess_board_state.black_positions.remove((new_move.piece.position[0], new_move.piece.position[1]))     
            chess_board_state.black_positions.append((new_move.new_position[0], new_move.new_position[1]))       
            if chess_board_state.white_positions.count((new_move.new_position[0], new_move.new_position[1])) > 0:
                chess_board_state.white_positions.remove((new_move.new_position[0], new_move.new_position[1]))
            if new_move.piece.type == "K":
                chess_board_state.king_positions[1] = new_move.new_position

        #See if move is castle
        self.last_move_castle = False if update_state_only else self.last_move_castle
        self.last_move_en_passant = False if update_state_only else self.last_move_en_passant 
        if new_move.castle:
            old_rook_pos = new_move.castle_rook_move.piece.position[0] * self.files +  new_move.castle_rook_move.piece.position[1]
            new_rook_pos = new_move.castle_rook_move.new_position[0] * self.files +  new_move.castle_rook_move.new_position[1]
            chess_board_state.piece_board[new_rook_pos] = self.piece_board[old_rook_pos]
            chess_board_state.piece_board[old_rook_pos] = None
            self.last_move_castle = True if update_state_only else self.last_move_castle
            if chess_board_state.whites_turn:
                chess_board_state.white_positions.remove((new_move.castle_rook_move.piece.position[0], new_move.castle_rook_move.piece.position[1]))
                chess_board_state.white_positions.append((new_move.castle_rook_move.new_position[0], new_move.castle_rook_move.new_position[1]))
            else:
                chess_board_state.black_positions.remove((new_move.castle_rook_move.piece.position[0], new_move.castle_rook_move.piece.position[1]))
                chess_board_state.black_positions.append((new_move.castle_rook_move.new_position[0], new_move.castle_rook_move.new_position[1]))
            chess_board_state.piece_board[new_rook_pos].position = new_move.castle_rook_move.new_position
            
        #See if move is enpassant
        elif new_move.en_passant:
            pos = new_move.en_passant_pawn.position[0] * self.files +  new_move.en_passant_pawn.position[1]
            chess_board_state.piece_board[pos] = None
            if chess_board_state.whites_turn:
                chess_board_state.black_positions.remove((new_move.en_passant_pawn.position[0], new_move.en_passant_pawn.position[1]))
            else:
                chess_board_state.white_positions.remove((new_move.en_passant_pawn.position[0], new_move.en_passant_pawn.position[1]))
            self.last_move_en_passant = True if update_state_only else self.last_move_en_passant 

        #Pawn Promotion
        if new_move.promotion:
            chess_board_state.piece_board[new_pos].type = new_move.promotion_type
            chess_board_state.piece_board[new_pos].set_type_functions()

        #Update Piece
        chess_board_state.piece_board[new_pos].position = new_move.new_position

        #Update half and full move
        chess_board_state.half_move = 0 if captured else chess_board_state.half_move + 1
        chess_board_state.full_move = chess_board_state.full_move + 1 if chess_board_state.whites_turn else chess_board_state.full_move 

        #Update Turn
        chess_board_state.whites_turn = False if chess_board_state.whites_turn else True
        return chess_board_state

    def check_move_for_check(self, new_move: ChessMove, chess_board_state: ChessBoardState) -> bool:
        """Creates a new board to simulate new move to see if other team is able to check.

            Returns: True if other team is able to check our king.
        """
        new_piece_board, other_teams_positions, new_king_positions = self._simulate_move(new_move, chess_board_state)
        for r, f in other_teams_positions:
            piece: ChessPiece = new_piece_board[r * self.files + f]
            if piece.get_piece_check(self, new_piece_board, new_king_positions):
                return True
        return False
    
    def calc_check_status(self, chess_board_state: ChessBoardState) -> "ChessBoardState":
        """Calculates the check status of the current board. The move list must be up to date.

            Returns: Self for chaining.
        """
        if chess_board_state.whites_turn:
            #Get in check
            in_check = False
            for r, f in chess_board_state.black_positions:
                piece: ChessPiece = chess_board_state.piece_board[r * self.files + f]
                if piece.get_piece_check(self, chess_board_state.piece_board, chess_board_state.king_positions):
                    in_check = True
            #Calc check status 0 = Stale, 1 = Check, 2 = Checkmate
            if in_check:
                if len(chess_board_state.white_moves) == 0:
                    chess_board_state.check_status = -2
                else:
                    chess_board_state.check_status = -1
            else:
                if len(chess_board_state.white_moves) == 0:
                    chess_board_state.check_status = 0
                else:
                    chess_board_state.check_status = None
        else:
            #Get in check
            in_check = False
            for r, f in chess_board_state.white_positions:
                piece: ChessPiece = chess_board_state.piece_board[r * self.files + f]
                if piece.get_piece_check(self, chess_board_state.piece_board, chess_board_state.king_positions):
                    in_check = True
            #Calc check status 0 = Stale, 1 = Check, 2 = Checkmate
            if in_check:
                if len(chess_board_state.black_moves) == 0:
                    chess_board_state.check_status = 2
                else:
                    chess_board_state.check_status = 1
            else:
                if len(chess_board_state.black_moves) == 0:
                    chess_board_state.check_status = 0
                else:
                    chess_board_state.check_status = None
        return chess_board_state
    
    def _calc_new_team_moves(self, chess_board_state: ChessBoardState) -> "ChessBoardState":
        if chess_board_state.whites_turn:
            new_moves = []
            for r, f in chess_board_state.white_positions:
                white_piece: ChessPiece = chess_board_state.piece_board[r * self.files + f]
                new_moves = new_moves + white_piece.calc_moves_attacks(self, chess_board_state).moves
            chess_board_state.white_moves = new_moves
            chess_board_state.black_moves = []
        else:
            new_moves = []
            for r, f in self.black_positions:
                black_piece: ChessPiece = self.piece_board[r * self.files + f]
                new_moves = new_moves + black_piece.calc_moves_attacks(self, chess_board_state).moves
            chess_board_state.black_moves = new_moves
            chess_board_state.white_moves = []
        return chess_board_state

    def move_piece(self, new_move: ChessMove, chess_board_state: ChessBoardState, create_new_state: bool = False) -> "ChessBoardState":
        #Get new copy of board
        new_state = None
        if create_new_state:
            new_state = ChessBoardState(chess_board_state, self.ranks, self.files)
        else:
            new_state = self.state

        #Update Castle Str
        if new_move.piece.type == "K":
            if new_state.whites_turn:
                new_state.castle_avail = new_state.castle_avail.replace('K', '').replace('Q','')
            else:
                new_state.castle_avail = new_state.castle_avail.replace('k', '').replace('q','')
        elif new_move.piece.type == "R":
            if new_state.whites_turn:
                if new_move.piece.position[1] == 0:
                    new_state.castle_avail = new_state.castle_avail.replace('Q', '')
                elif new_move.piece.position[1] == new_state.files-1:
                    new_state.castle_avail = new_state.castle_avail.replace('K', '')
            else:
                if new_move.piece.position[1] == 0:
                    new_state.castle_avail = new_state.castle_avail.replace('q', '')
                elif new_move.piece.position[1] == new_state.files-1:
                    new_state.castle_avail = new_state.castle_avail.replace('k', '')
        new_state.castle_avail = '-' if new_state.castle_avail == '' else new_state.castle_avail
        
        #Update En passant str
        new_state.en_passant = "-"
        if new_move.piece.type == "P":
            if new_move.new_position[0] - new_move.piece.position[0] == 2:
                r = new_move.piece.position[0] + 1
                rank = new_state.utils.get_rank_from_number(r, new_state.ranks)
                file = new_state.utils.get_file_from_number(new_move.new_position[1])
                new_state.en_passant = file + rank
            elif new_move.new_position[0] - new_move.piece.position[0] == -2:
                r = new_move.piece.position[0] - 1
                rank = new_state.utils.get_rank_from_number(r, new_state.ranks)
                file = new_state.utils.get_file_from_number(new_move.new_position[1])
                new_state.en_passant = file + rank

        #Execute Move
        new_state = self._new_move(new_move, new_state, create_new_state)

        #Update Current Teams Moves
        new_state = self._calc_new_team_moves(new_state)

        #Update Check Status
        new_state = self.calc_check_status(new_state)

        return new_state
    
    


    