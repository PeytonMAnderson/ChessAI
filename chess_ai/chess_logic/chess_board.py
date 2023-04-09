from copy import copy
from .chess_piece import ChessPiece, get_type_functions
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
            self.piece_board = board_state.piece_board[:]
            self.white_positions = board_state.white_positions[:]
            self.black_positions = board_state.black_positions[:]
            self.white_moves = board_state.white_moves[:]
            self.black_moves = board_state.black_moves[:]
            self.king_positions = board_state.king_positions[:]


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
        self._calc_new_team_moves(self.state)
        self.calc_check_status(self.state)

        #Return self
        return self
    
    def board_to_fen(self, board_state: ChessBoardState = None) -> str:
        """Generates a FEN string from the current board.

            Returns: FEN string.
        """
        bs = board_state if board_state is not None else self.state
        rank_index = 0
        file_index = 0

        rank_str = ""
        #Go Through ranks
        while rank_index < self.ranks:

            #Go Through Files
            file_str_total: str = ""
            file_str_prev: str = ''
            file_index = 0
            while file_index < self.files:

                #Get piece from board
                loc = rank_index * self.files + file_index
                piece: ChessPiece = bs.piece_board[loc]

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
        color_str = "w" if bs.whites_turn else "b"
        return rank_str + " " + color_str + " " + bs.castle_avail + " " + bs.en_passant + " " + str(bs.half_move) + " " + str(bs.full_move)
    
    def uci_to_move(self, uci: str, board_state: ChessBoardState) -> ChessMove | None:
        move_list = board_state.white_moves if board_state.whites_turn else board_state.black_moves
        rank1, file1, rank2, file2 = uci[0], uci[1], uci[2], uci[3]
        r1, f1 = self.utils.get_number_from_rank(rank1, self.ranks), self.utils.get_number_from_file(file1, self.files)
        r2, f2 = self.utils.get_number_from_rank(rank2, self.ranks), self.utils.get_number_from_file(file2, self.files)
        move: ChessMove
        for move in move_list:
            ro, fo = move.piece.position
            rf, ff = move.new_position
            if (r1, f1) == (ro, fo) and (r2, f2) == (rf, ff):
                return move
        return None

    def move_to_uci(self, move: ChessMove) -> str:
        r1, f1 = move.piece.position
        r2, f2 = move.new_position
        rank1, file1 = self.utils.get_rank_from_number(r1, self.ranks), self.utils.get_file_from_number(f1, self.files)
        rank2, file2 = self.utils.get_rank_from_number(r2, self.ranks), self.utils.get_file_from_number(f2, self.files)
        promotion = ""
        if move.promotion:
            promotion = move.promotion_type.lower()
        return file1 + rank1 + file2 + rank2 + promotion

    def _simulate_move(self, new_move: ChessMove, chess_board_state: ChessBoardState) -> tuple[list, list, list, list, bool]:

        new_piece_board = chess_board_state.piece_board.copy()
        new_king_positions = chess_board_state.king_positions.copy()

        #Perform Move
        old_pos = new_move.piece.position[0] * self.files +  new_move.piece.position[1]
        new_pos = new_move.new_position[0] * self.files +  new_move.new_position[1]
        new_piece_board[new_pos] = new_piece_board[old_pos]
        new_piece_board[old_pos] = None

        #Update Data Trackers
        if chess_board_state.whites_turn:
            if new_move.piece.type == "K":
                new_king_positions[0] = new_move.new_position
        else:     
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

        #Update Turn
        return new_piece_board, new_king_positions
        
    
    def _new_move(self, new_move: ChessMove,  chess_board_state: ChessBoardState, update_self: bool) -> "ChessBoardState":
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
        self.last_move_castle = self.last_move_castle if update_self else False
        self.last_move_en_passant = self.last_move_en_passant if update_self else False
        if new_move.castle:
            old_rook_pos = new_move.castle_rook_move.piece.position[0] * self.files +  new_move.castle_rook_move.piece.position[1]
            new_rook_pos = new_move.castle_rook_move.new_position[0] * self.files +  new_move.castle_rook_move.new_position[1]
            chess_board_state.piece_board[new_rook_pos] = chess_board_state.piece_board[old_rook_pos]
            chess_board_state.piece_board[old_rook_pos] = None
            self.last_move_castle = self.last_move_castle if update_self else True
            if chess_board_state.whites_turn:
                chess_board_state.white_positions.remove((new_move.castle_rook_move.piece.position[0], new_move.castle_rook_move.piece.position[1]))
                chess_board_state.white_positions.append((new_move.castle_rook_move.new_position[0], new_move.castle_rook_move.new_position[1]))
            else:
                chess_board_state.black_positions.remove((new_move.castle_rook_move.piece.position[0], new_move.castle_rook_move.piece.position[1]))
                chess_board_state.black_positions.append((new_move.castle_rook_move.new_position[0], new_move.castle_rook_move.new_position[1]))

            #Update Piece
            if update_self:
                chess_board_state.piece_board[new_rook_pos].position = new_move.castle_rook_move.new_position
            #Create a new piece and replace the old reference
            else:
                rook: ChessPiece = chess_board_state.piece_board[new_pos]
                chess_board_state.piece_board[new_rook_pos] = ChessPiece(rook.value, rook.type, rook.is_white, new_move.castle_rook_move.new_position)
            
        #See if move is enpassant
        elif new_move.en_passant:
            pos = new_move.en_passant_pawn.position[0] * self.files +  new_move.en_passant_pawn.position[1]
            chess_board_state.piece_board[pos] = None
            if chess_board_state.whites_turn:
                chess_board_state.black_positions.remove((new_move.en_passant_pawn.position[0], new_move.en_passant_pawn.position[1]))
            else:
                chess_board_state.white_positions.remove((new_move.en_passant_pawn.position[0], new_move.en_passant_pawn.position[1]))
            self.last_move_en_passant = self.last_move_en_passant  if update_self else True
        
        #Update this board, else update the copy
        if update_self:

            #Pawn Promotion
            if new_move.promotion:
                piece: ChessPiece = chess_board_state.piece_board[new_pos]
                piece.position = new_move.new_position
                piece.type = new_move.promotion_type
                piece.move_function = get_type_functions(new_move.promotion_type)
            #Create a new Piece and replace the old reference
            else:
                piece: ChessPiece = chess_board_state.piece_board[new_pos]
                chess_board_state.piece_board[new_pos] = ChessPiece(piece.value, piece.type, piece.is_white, new_move.new_position)
            
        else:
            
            #Pawn Promotion
            if new_move.promotion:
                piece: ChessPiece = chess_board_state.piece_board[new_pos]
                value = self.utils._calc_piece_value(piece_type=new_move.promotion_type, is_white=piece.is_white)
                chess_board_state.piece_board[new_pos] = ChessPiece(value, new_move.promotion_type, piece.is_white, new_move.new_position)
            #Create a new Piece and replace the old reference
            else:
                piece: ChessPiece = chess_board_state.piece_board[new_pos]
                chess_board_state.piece_board[new_pos] = ChessPiece(piece.value, piece.type, piece.is_white, new_move.new_position)

        #Update half and full move
        chess_board_state.half_move = 0 if captured else chess_board_state.half_move + 1
        chess_board_state.full_move = chess_board_state.full_move + 1 if chess_board_state.whites_turn else chess_board_state.full_move 

        #Update Turn
        chess_board_state.whites_turn = False if chess_board_state.whites_turn else True
        return chess_board_state
    
    def _get_king_vision_in_check(self, piece_board: list, king_positions: list, whites_turn: bool):
        #Get Simulated Move
        king_position = king_positions[0] if whites_turn else king_positions[1]
        #Check Rook, Queen, King type Moves
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for rd, fd in directions:
            rank_i, file_i = king_position[0] + rd, king_position[1] + fd
            while rank_i >= 0 and rank_i < self.ranks and file_i >= 0 and file_i < self.files:
                new_loc = rank_i * self.files + file_i
                defending_piece: ChessPiece = piece_board[new_loc]
                if defending_piece is not None:
                    if defending_piece.is_white != whites_turn:
                        #If a rook or queen exist in the unblocked rank/file, they are causing check.
                        if defending_piece.type == "R" or defending_piece.type == "Q":
                            return True
                        #If the other King is able to "attack"
                        elif defending_piece.type == "K" and abs(rank_i - king_position[0]) <= 1 and abs(file_i - king_position[1]) <= 1:
                            return True
                    break
                rank_i, file_i = rank_i + rd, file_i + fd

        #Check Bishop, Queen, Pawn, King Type moves
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for rd, fd in directions:
            rank_i, file_i = king_position[0] + rd, king_position[1] + fd
            while rank_i >= 0 and rank_i < self.ranks and file_i >= 0 and file_i < self.files:
                new_loc = rank_i * self.files + file_i
                defending_piece: ChessPiece = piece_board[new_loc]
                if defending_piece is not None:
                    if defending_piece.is_white != whites_turn:
                        #If an enemy bishop or Q exist in the unblocked diagonal, they are causing check.
                        if defending_piece.type == "B" or defending_piece.type == "Q":
                            return True
                        elif defending_piece.type == "P":
                            #Black can attack with pawn if black pawn is 1 rank up, and 1 file over left or right
                            if whites_turn and king_position[0] == rank_i + 1 and abs(king_position[1] - file_i) == 1:
                                return True
                            #White can attack with pawn if black king is 1 rank down and 1 file over left or right
                            elif not whites_turn and king_position[0] == rank_i - 1 and abs(king_position[1] - file_i) == 1:
                                return True
                        #If the other King is able to "attack"
                        elif defending_piece.type == "K" and abs(rank_i - king_position[0]) <= 1 and abs(file_i - king_position[1]) <= 1:
                            return True
                    break
                rank_i, file_i = rank_i + rd, file_i + fd
        #Check Knight
        possible_locations = [(2,1), (1,2), (2,-1), (1,-2), (-2,1), (-1,2), (-2,-1), (-1,-2)]
        rank_i, file_i = king_position
        for rd, fd in possible_locations:
            r, f = king_position[0]+ rd, king_position[1] + fd
            if r >= 0 and r < self.ranks and f >= 0 and f < self.files:
                new_loc = r * self.files + f
                defending_piece: ChessPiece = piece_board[new_loc]
                if defending_piece is None or defending_piece.is_white == whites_turn:
                    continue
                if defending_piece.type == "N":
                    return True
        return False

    def check_move_for_check(self, new_move: ChessMove, chess_board_state: ChessBoardState) -> bool:
        """Creates a new board to simulate new move to see if other team is able to check.

            Returns: True if other team is able to check our king.
        """
        #Get Simulated Move
        new_piece_board, new_king_positions = self._simulate_move(new_move, chess_board_state)
        return self._get_king_vision_in_check(new_piece_board, new_king_positions, chess_board_state.whites_turn)

    
    def calc_check_status(self, chess_board_state: ChessBoardState, check_status_semi_updated: bool = False) -> "ChessBoardState":
        """Calculates the check status of the current board. The move list must be up to date.

            Returns: Self for chaining.
        """
        #Get If Currently In Check
        in_check:bool
        if check_status_semi_updated:
            #If Check status is in favor of Black and currently whites turn, or Check Status in favor of white and currently blacks turn, else no check
            in_check = True if chess_board_state.check_status == 1 else False
        else:
            #Calculate check status manually
            in_check = self._get_king_vision_in_check(chess_board_state.piece_board, chess_board_state.king_positions, chess_board_state.whites_turn)

        if chess_board_state.whites_turn:
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
            for r, f in chess_board_state.black_positions:
                black_piece: ChessPiece = chess_board_state.piece_board[r * self.files + f]
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
                elif new_move.piece.position[1] == self.files-1:
                    new_state.castle_avail = new_state.castle_avail.replace('K', '')
            else:
                if new_move.piece.position[1] == 0:
                    new_state.castle_avail = new_state.castle_avail.replace('q', '')
                elif new_move.piece.position[1] == self.files-1:
                    new_state.castle_avail = new_state.castle_avail.replace('k', '')
        new_state.castle_avail = '-' if new_state.castle_avail == '' else new_state.castle_avail
        
        #Update En passant str
        new_state.en_passant = "-"
        if new_move.piece.type == "P":
            if new_move.new_position[0] - new_move.piece.position[0] == 2:
                r = new_move.piece.position[0] + 1
                rank = self.utils.get_rank_from_number(r, self.ranks)
                file = self.utils.get_file_from_number(new_move.new_position[1])
                new_state.en_passant = file + rank
            elif new_move.new_position[0] - new_move.piece.position[0] == -2:
                r = new_move.piece.position[0] - 1
                rank = self.utils.get_rank_from_number(r, self.ranks)
                file = self.utils.get_file_from_number(new_move.new_position[1])
                new_state.en_passant = file + rank

        #Execute Move
        new_state = self._new_move(new_move, new_state, not create_new_state)

        #Get Check status for generating new moves
        in_check = self._get_king_vision_in_check(new_state.piece_board, new_state.king_positions, new_state.whites_turn)
        new_state.check_status = 1 if in_check else None

        #Update Current Teams Moves
        new_state = self._calc_new_team_moves(new_state)

        #Update Check Status
        new_state = self.calc_check_status(new_state, True)

        return new_state
    
    


    