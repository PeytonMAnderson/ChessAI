
from typing import Callable

from .chess_move import ChessMove

def _get_pawn_attacks(piece, board, board_state) -> list[ChessMove]:
    rank_i_old, file_i_old = piece.position
    rank_diff = -1 if piece.is_white else 1
    attacks = []

    #enpassant
    e_r, e_f = None, None
    if len(board_state.en_passant) == 2:
        e_r = board.utils.get_number_from_rank(board_state.en_passant[1], board.ranks)
        e_f = board.utils.get_number_from_file(board_state.en_passant[0])

    files = [-1, 1]

    #Check left and right
    for file_diff in files:
        
        #Filter out moves that are out of bounds
        r, f = rank_i_old + rank_diff, file_i_old + file_diff
        if f < 0 or f >= board.files:
            continue

        #Check if attackable
        defending_piece: ChessPiece = board_state.piece_board[r * board.files + f]
        if defending_piece is not None and defending_piece.is_white != piece.is_white:
            new_move = ChessMove(piece, (r, f))
            if board.check_move_for_check(new_move, board_state) is False:
                if (r == 0 and piece.is_white) or (r == board.ranks - 1 and not piece.is_white):
                    new_move.promotion = True
                    new_move.promotion_type = "Q"
                attacks.append(new_move)

        #Else try en passant
        elif e_r is not None and e_f is not None:
            if (e_r, e_f) == (r, f):
                if (e_r == 2 and piece.is_white) or (e_r == board.ranks-3 and not piece.is_white):
                    en_passant_piece = board_state.piece_board[rank_i_old * board.files + f]
                    new_move = ChessMove(piece, (r, f), en_passant=True, en_passant_pawn=en_passant_piece)                
                    if board.check_move_for_check(new_move, board_state) is False:
                        if (r == 0 and piece.is_white) or (r == board.ranks - 1 and not piece.is_white):
                            new_move.promotion = True
                            new_move.promotion_type = "Q"
                        attacks.append(new_move)
    return attacks
        


def _get_pawn_moves(piece, board, board_state) -> tuple[list, list]:
        """Get all moves that the piece can take including captures.

            Returns: List of moves and list of attacks.
        """
        moves = []
        attacks = []
        rank_i_old, file_i_old = piece.position
        rank_diff = -1 if piece.is_white else 1

        #Stay bounds
        if (rank_i_old == 0 and piece.is_white) or (rank_i_old == board.ranks - 1 and not piece.is_white):
            return moves, attacks

        #Get basic moves
        new_loc = (rank_i_old + rank_diff) * board.files + file_i_old
        if board_state.piece_board[new_loc] is None:
            new_move = ChessMove(piece, (rank_i_old + rank_diff, file_i_old))
            if board.check_move_for_check(new_move, board_state) is False:
                if (rank_i_old + rank_diff == 0 and piece.is_white) or (rank_i_old + rank_diff == board.ranks - 1 and not piece.is_white):
                    new_move.promotion = True
                    new_move.promotion_type = "Q"
                moves.append(new_move)
        if len(moves) == 1:
            if (rank_i_old == 1 and not piece.is_white) or (rank_i_old == board.ranks - 2 and piece.is_white):
                new_loc = (rank_i_old + rank_diff * 2) * board.files + file_i_old
                if board_state.piece_board[new_loc] is None:
                    new_move = ChessMove(piece, (rank_i_old + rank_diff * 2, file_i_old))
                    if board.check_move_for_check(new_move, board_state) is False:
                        if (rank_i_old + rank_diff == 0 and piece.is_white) or (rank_i_old + rank_diff == board.ranks - 1 and not piece.is_white):
                            new_move.promotion = True
                            new_move.promotion_type = "Q"
                        moves.append(new_move)
        attacks = _get_pawn_attacks(piece, board, board_state)
        return moves + attacks, attacks

def _get_knight_moves(piece, board, board_state) -> tuple[list, list]:
    """Get all moves that the piece can take including captures.

        Returns: List of moves and list of attacks.
    """
    moves = []
    attacks = []
    rank_i_old, file_i_old = piece.position

    #Checks                  top right,     top left,      bottom_right,     bottom_left
    possible_locations = [(2,1), (1,2), (2,-1), (1,-2), (-2,1), (-1,2), (-2,-1), (-1,-2)]
    for r, f in possible_locations:
        #Stay bounds
        new_r, new_f = rank_i_old + r, file_i_old + f
        if new_r < 0 or new_r >= board.ranks or new_f < 0 or new_f >= board.files:
            continue
        #Check captures
        new_loc = (rank_i_old + r) * board.files + file_i_old + f
        defending_piece: ChessPiece = board_state.piece_board[new_loc]
        if defending_piece is None:
            new_move = ChessMove(piece, (rank_i_old + r, file_i_old + f))
            if board.check_move_for_check(new_move, board_state) is False:
                moves.append(new_move)
        elif defending_piece.is_white != piece.is_white:
            new_move = ChessMove(piece, (rank_i_old + r, file_i_old + f))
            if board.check_move_for_check(new_move, board_state) is False:
                moves.append(new_move)
                attacks.append(new_move)
    return moves, attacks

def _get_bishop_moves(piece, board, board_state) -> tuple[list, list]:
    """Get all moves that the piece can take including captures.

        Returns: List of moves and list of attacks.
    """
    moves = []
    attacks = []

    #Check each diagonal
    direction = [(1,1), (1,-1), (-1,1), (-1,-1)]
    for dr, df in direction:
        rank_i, file_i = piece.position[0] + dr, piece.position[1] + df
        while  rank_i >= 0 and rank_i < board.ranks and file_i >= 0 and file_i < board.files:
            #Check captures
            new_loc = rank_i * board.files + file_i
            defending_piece: ChessPiece = board_state.piece_board[new_loc]
            if defending_piece is None:
                new_move = ChessMove(piece, (rank_i, file_i))
                if board.check_move_for_check(new_move, board_state) is False:
                    moves.append(new_move)
            elif defending_piece.is_white != piece.is_white:
                new_move = ChessMove(piece, (rank_i, file_i))
                if board.check_move_for_check(new_move, board_state) is False:
                    moves.append(new_move)
                    attacks.append(new_move)
                break
            else:
                break
            rank_i += dr
            file_i += df
    return moves, attacks

def _get_rook_moves(piece, board, board_state) -> tuple[list, list]:
    """Get all moves that the piece can take including captures.

        Returns: List of moves and list of attacks.
    """
    moves = []
    attacks = []

    #Check each diagonal
    direction = [(1,0), (0,1), (-1,0), (0,-1)]
    for dr, df in direction:
        rank_i, file_i = piece.position[0] + dr, piece.position[1] + df
        while  rank_i >= 0 and rank_i < board.ranks and file_i >= 0 and file_i < board.files:
            #Check captures
            new_loc = rank_i * board.files + file_i
            defending_piece: ChessPiece = board_state.piece_board[new_loc]
            if defending_piece is None:
                new_move = ChessMove(piece, (rank_i, file_i))
                if board.check_move_for_check(new_move, board_state) is False:
                    moves.append(new_move)
            elif defending_piece.is_white != piece.is_white:
                new_move = ChessMove(piece, (rank_i, file_i))
                if board.check_move_for_check(new_move, board_state) is False:
                    moves.append(new_move)
                    attacks.append(new_move)
                break
            else:
                break
            rank_i += dr
            file_i += df
    return moves, attacks

def _get_queen_moves(piece, board, board_state) -> tuple[list, list]:
    """Get all moves that the piece can take including captures.

        Returns: List of moves and list of attacks.
    """
    moves, attacks = _get_bishop_moves(piece, board, board_state)
    moves_2, attacks_2 = _get_rook_moves(piece, board, board_state)
    return moves + moves_2, attacks + attacks_2

def _get_king_castle(piece, board, board_state, can_castle: tuple[bool, bool]) -> list:
    #Add Castling Moves
    moves = []
    king_side = False
    k_r, k_f = piece.position
    for castle in can_castle:
        #If all checks for check pass
        if not castle:
            king_side = True
            continue

        #Find castling availability from the castle_avail string
        castle_str = "K" if king_side else "Q"
        castle_str_case = castle_str if piece.is_white else castle_str.lower()
        if board_state.castle_avail.find(castle_str_case) < 0:
            king_side = True
            continue

        #See if lane is open to rook
        rook: ChessPiece = None
        f_diff = 1 if king_side else -1
        f_r = board.files - 1 if king_side else 0
        r, f = k_r, k_f + f_diff
        while f >= 0 and f < board.files:
            #If location is empty
            new_loc = r * board.files + f
            defending_piece: ChessPiece = board_state.piece_board[new_loc]
            if defending_piece is None:
                f += f_diff
                continue
            #If piece is rook, and the rook is the same color, and the rook is on the edge
            if defending_piece.type == "R" and defending_piece.is_white == piece.is_white and f_r == f:
                rook = defending_piece
            break
        
        #Check if new king position is safe
        castle_safe = True
        if piece.is_white:
            for move in board_state.black_moves:
                if (move.new_position[0], move.new_position[1]) == (k_r, k_f + f_diff * 2):
                    castle_safe = False
                    break
        else:
            for move in board_state.white_moves:
                if (move.new_position[0], move.new_position[1]) == (k_r, k_f + f_diff * 2):
                    castle_safe = False
                    break

        #If castle_safe, create castle move
        if castle_safe and rook is not None:
            moves.append(ChessMove(piece, (k_r, k_f + f_diff * 2), castle=True, castle_rook_move=ChessMove(rook, (k_r, k_f + f_diff))))
        king_side = True
    return moves

def _get_king_moves(piece, board, board_state) -> tuple[list, list]:
    """Get all moves that the piece can take including captures.

        Returns: List of moves and list of attacks.
    """
    moves = []
    attacks = []
    r_k, f_k = piece.position
    r_tl, f_tl = r_k - 1, f_k - 1
    can_castle = [True, True] if board_state.check_status is None else [False, False]

    #Start at top left and check in 3 x 3 grid
    for ri in range(3):
        for fi in range(3):

            #Check if current location is the kings
            r, f = r_tl + ri, f_tl + fi
            if r == r_k and f == f_k:
                continue

            #Filter position if out of bounds:
            if r < 0 or r >= board.ranks or f < 0 or f >= board.files:
                continue

            #Add Moves and Attacks
            new_loc = r * board.files + f
            defending_piece: ChessPiece = board_state.piece_board[new_loc]
            new_move = ChessMove(piece, (r, f))

            #If move does not create check
            if board.check_move_for_check(new_move, board_state) is False:
                if defending_piece is None:
                    moves.append(new_move)
                elif defending_piece.is_white != piece.is_white:
                    moves.append(new_move)
                    attacks.append(new_move) 
            #If move does create check, remove castling if left of king or right of king
            else:
                if r == r_k:
                    can_castle[1] = False if f == f_k + 1 else can_castle[1]
                    can_castle[0] = False if f == f_k - 1 else can_castle[0]

    moves = moves + _get_king_castle(piece, board, board_state, can_castle)
    return moves, attacks

def get_type_functions(piece_type: str = None) -> tuple[Callable, Callable]:
    """Checks they type of piece located at (rank_i_old, file_i_old) and determines which types of move check function to return.

        Returns: Check Moves Function specific to the type of piece at (rank_i_old, file_i_old)
    """
    p_str = piece_type if piece_type is not None else "P"
    move_function = _get_pawn_moves
    if p_str == "P":
        return move_function
    elif p_str == "N":
        move_function  = _get_knight_moves
    elif p_str == "B":
        move_function  = _get_bishop_moves
    elif p_str == "R":
        move_function  = _get_rook_moves
    elif p_str == "Q":
        move_function  = _get_queen_moves
    elif p_str == "K":
        move_function  = _get_king_moves
    return move_function

class ChessPiece:
    def __init__(self, 
                 value: int = 0, 
                 type: str = "", 
                 is_white: bool = None, 
                 position: tuple = (0, 0), 
    *args, **kwargs) -> None:
        self.value = value
        self.type = type
        self.is_white = is_white
        self.position = position
        self.moves: list[ChessMove]
        self.attacks = list[ChessMove]
        self.move_function = get_type_functions(type)

    def calc_moves_attacks(self, board, board_state) -> "ChessPiece":
        """Calculates all moves and all attacks the piece is able to make.

            Returns piece for chaining
        """
        self.moves, self.attacks = self.move_function(self, board, board_state)
        return self
    