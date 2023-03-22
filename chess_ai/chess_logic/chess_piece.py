
#from .chess_board import ChessBoard

from typing import Callable

def get_pawn_attacks(rank_i_old: int, file_i_old: int, is_white: bool, board) -> list:
    """Get all attack moves that the piece will capture.

        Returns: List of attacking moves.
    """
    attacks = []
    rank_diff = -1 if is_white else 1

    #Get attack left
    if file_i_old - 1 >= 0:
        defending_piece: ChessPiece = board.piece_board[(rank_i_old + rank_diff) * board.files + file_i_old - 1]
        if defending_piece.is_white != is_white:
            attacks.append((rank_i_old, file_i_old, rank_i_old + rank_diff, file_i_old - 1))
    #Get attack right
    if file_i_old + 1 < board.files:
        defending_piece: ChessPiece = board.piece_board[(rank_i_old + rank_diff) * board.files + file_i_old + 1]
        if defending_piece.is_white != is_white:
            attacks.append((rank_i_old, file_i_old, rank_i_old + rank_diff, file_i_old + 1))

def get_pawn_moves(rank_i_old: int, file_i_old: int, is_white: bool, board) -> tuple[list, list]:
    """Get all moves that the piece can take including captures.

        Returns: List of moves and list of attacks.
    """
    moves = []
    rank_diff = -1 if is_white else 1

    #Stay bounds
    if rank_i_old == 0 or rank_i_old == board.ranks - 1:
        return []

    #Get basic moves
    new_loc = (rank_i_old + rank_diff) * board.files + file_i_old
    if board.piece_board[new_loc] is None:
        moves.append((rank_i_old, file_i_old, rank_i_old + rank_diff, file_i_old))
    if len(moves) == 1:
        if rank_i_old == 1 or rank_i_old == board.ranks - 2:
            new_loc = (rank_i_old + rank_diff * 2) * board.files + file_i_old
            if board.piece_board[new_loc] is None:
                moves.append((rank_i_old, file_i_old, rank_i_old + rank_diff, file_i_old))

    #Get attack moves
    attacks = get_pawn_attacks(rank_i_old, file_i_old, is_white, board)
    moves = moves + attacks
    return moves, attacks


def get_knight_moves(rank_i_old: int, file_i_old: int, is_white: bool, board) -> tuple[list, list]:
    """Get all moves that the piece can take including captures.

        Returns: List of moves and list of attacks.
    """
    moves = []
    attacks = []

    #Checks                  top right,     top left,      bottom_right,     bottom_left
    possible_locations = [(2,1), (1,2), (2,-1), (1,-2), (-2,1), (-1,2), (-2,-1), (-1,-2)]
    for r, f in possible_locations:
        #Stay bounds
        new_r, new_f = rank_i_old + r, file_i_old + f
        if new_r < 0 or new_r >= board.ranks or new_f < 0 or new_f >= board.files:
            continue

        #Check captures
        new_loc = (rank_i_old + r) * board.files + file_i_old + f
        defending_piece: ChessPiece = board.piece_board[new_loc]
        if defending_piece is None:
            moves.append((rank_i_old, file_i_old, rank_i_old + r, file_i_old + f))
        elif defending_piece.is_white != is_white:
            moves.append((rank_i_old, file_i_old, rank_i_old + r, file_i_old + f))
            attacks.append((rank_i_old, file_i_old, rank_i_old + r, file_i_old + f))
    
    return moves, attacks

def get_bishop_moves(rank_i_old: int, file_i_old: int, is_white: bool, board) -> tuple[list, list]:
    """Get all moves that the piece can take including captures.

        Returns: List of moves and list of attacks.
    """
    moves = []
    attacks = []

    #Check each diagonal
    rank_i, file_i = rank_i_old, file_i_old
    direction = [(1,1), (1,-1), (-1,1), (-1,-1)]
    for dr, df in direction:
        rank_i, file_i = rank_i + dr, file_i + df
        while  rank_i >= 0 and rank_i < board.ranks and file_i >= 0 and file_i < board.files:
            #Check captures
            new_loc = rank_i * board.files + file_i
            defending_piece: ChessPiece = board.piece_board[new_loc]
            if defending_piece is None:
                moves.append((rank_i_old, file_i_old, rank_i, file_i))
            elif defending_piece.is_white != is_white:
                moves.append((rank_i_old, file_i_old, rank_i, file_i))
                attacks.append((rank_i_old, file_i_old, rank_i, file_i))
                break
            rank_i + dr
            file_i + df
    return moves, attacks

def get_rook_moves(rank_i_old: int, file_i_old: int, is_white: bool, board) -> tuple[list, list]:
    """Get all moves that the piece can take including captures.

        Returns: List of moves and list of attacks.
    """
    moves = []
    attacks = []

    #Check each diagonal
    rank_i, file_i = rank_i_old, file_i_old
    direction = [(1,0), (0,1), (-1,0), (0,-1)]
    for dr, df in direction:
        rank_i, file_i = rank_i + dr, file_i + df
        while  rank_i >= 0 and rank_i < board.ranks and file_i >= 0 and file_i < board.files:
            #Check captures
            new_loc = rank_i * board.files + file_i
            defending_piece: ChessPiece = board.piece_board[new_loc]
            if defending_piece is None:
                moves.append((rank_i_old, file_i_old, rank_i, file_i))
            elif defending_piece.is_white != is_white:
                moves.append((rank_i_old, file_i_old, rank_i, file_i))
                attacks.append((rank_i_old, file_i_old, rank_i, file_i))
                break
            rank_i + dr
            file_i + df
    return moves, attacks

def get_queen_moves(rank_i_old: int, file_i_old: int, is_white: bool, board) -> tuple[list, list]:
    """Get all moves that the piece can take including captures.

        Returns: List of moves and list of attacks.
    """
    moves, attacks = get_bishop_moves(rank_i_old, file_i_old, is_white, board)
    moves_2, attacks_2 = get_bishop_moves(rank_i_old, file_i_old, is_white, board)
    return moves + moves_2, attacks + attacks_2

def get_king_moves(rank_i_old: int, file_i_old: int, is_white: bool, board) -> tuple[list, list]:
    """Get all moves that the piece can take including captures.

        Returns: List of moves and list of attacks.
    """
    moves = []
    attacks = []
    ro, fo = rank_i_old - 1, file_i_old - 1
    for ri in range(3):
        for fi in range(3):
            if ri == 1 and fi == 1:
                continue
            r, f = ro + ri, fo + fi
            new_loc = r * board.files + f
            defending_piece: ChessPiece = board.piece_board[new_loc]

            #Filter move that causes check
            for _, _, rf, ff in board.black_moves:
                if (rf, ff) == (r, f):
                    continue

            #Add moves and attacks
            if defending_piece is None:
                moves.append((rank_i_old, file_i_old, r, f))
            elif defending_piece.is_white != is_white:
                moves.append((rank_i_old, file_i_old, r, f))
                attacks.append((rank_i_old, file_i_old, r, f))

    return moves, attacks

def get_type_move_function(piece_type: str) -> Callable:
    """Checks they type of piece located at (rank_i_old, file_i_old) and determines which types of move check function to return.

        Returns: Check Moves Function specific to the type of piece at (rank_i_old, file_i_old)
    """
    ret_function = get_pawn_moves
    if piece_type == "P":
        return ret_function
    elif piece_type == "N":
        ret_function = get_knight_moves
    elif piece_type == "B":
        ret_function = get_bishop_moves
    elif piece_type == "R":
        ret_function = get_rook_moves
    elif piece_type == "Q":
        ret_function = get_queen_moves
    elif piece_type == "K":
        ret_function = get_king_moves
    return ret_function

class ChessPiece:
    def __init__(self, value: int = 0, type: str = "", is_white: bool = None, position: tuple = (0, 0), flags: list = [], *args, **kwargs) -> None:
        self.value = value
        self.type = type
        self.is_white = is_white
        self.position = position
        self.flags = flags
        self.move_function = get_type_move_function(type)
        self.moves = []
        self.attacks = []

    def calc_positions(self, board) -> "ChessPiece":
        self.moves, self.attacks = self.move_function(self.position[0], self.position[1], self.is_white, board)
    