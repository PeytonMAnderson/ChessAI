
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
        
    #Get attack left
        if file_i_old - 1 >= 0:
            defending_piece = board_state.piece_board[(rank_i_old + rank_diff) * board.files + file_i_old - 1]

            #Check if can en passant
            can_en_passant = False
            if e_r is not None and e_f is not None:
                if (e_r, e_f) == (rank_i_old + rank_diff, file_i_old - 1):
                    if (e_r == 2 and piece.is_white) or (e_r == board.ranks-3 and not piece.is_white):
                        can_en_passant = True

            #Check if attackable
            if defending_piece is not None and defending_piece.is_white != piece.is_white:
                new_move = ChessMove(piece, (rank_i_old + rank_diff, file_i_old - 1))
                if board.check_move_for_check(new_move, board_state) is False:
                    if (rank_i_old + rank_diff == 0 and piece.is_white) or (rank_i_old + rank_diff == board.ranks - 1 and not piece.is_white):
                        new_move.promotion = True
                        new_move.promotion_type = "Q"
                    attacks.append(new_move)
            elif can_en_passant:
                en_passant_piece = board_state.piece_board[(rank_i_old) * board.files + file_i_old - 1]
                new_move = ChessMove(piece, (rank_i_old + rank_diff, file_i_old - 1), en_passant=True, en_passant_pawn=en_passant_piece)                
                if board.check_move_for_check(new_move, board_state) is False:
                    if (rank_i_old + rank_diff == 0 and piece.is_white) or (rank_i_old + rank_diff == board.ranks - 1 and not piece.is_white):
                        new_move.promotion = True
                        new_move.promotion_type = "Q"
                    attacks.append(new_move)

        #Get attack right
        if file_i_old + 1 < board.files:
            defending_piece = board_state.piece_board[(rank_i_old + rank_diff) * board.files + file_i_old + 1]

            #Check if can en passant
            can_en_passant = False
            if e_r is not None and e_f is not None:
                if (e_r, e_f) == (rank_i_old + rank_diff, file_i_old + 1):
                    if (e_r == 2 and piece.is_white) or (e_r == board.ranks-3 and not piece.is_white):
                        can_en_passant = True

            #Check if attackable
            if defending_piece is not None and defending_piece.is_white != piece.is_white:
                new_move = ChessMove(piece, (rank_i_old + rank_diff, file_i_old + 1))
                if board.check_move_for_check(new_move, board_state) is False:
                    attacks.append(new_move)
            elif can_en_passant:
                en_passant_piece = board_state.piece_board[(rank_i_old) * board.files + file_i_old + 1]  
                new_move = ChessMove(piece, (rank_i_old + rank_diff, file_i_old + 1), en_passant=True, en_passant_pawn=en_passant_piece)             
                if board.check_move_for_check(new_move, board_state) is False:
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

        return moves, _get_pawn_attacks(piece, board, board_state)

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

def _get_king_castle(piece, board, board_state, castle_check_king: bool, castle_check_queen: bool) -> list:
    #Add Castling Moves
    moves = []
    ro, fo = piece.position[0], piece.position[1]
    if board_state.check_status is not None:
        return moves
    if castle_check_king is False:
        #Make sure castling is available
        if board_state.castle_avail.find('K' if piece.is_white else 'k') >= 0:
            #Make sure file is open
            rook: ChessPiece = None
            file = fo + 1
            while file < board.files:
                new_loc = ro * board.files + file
                defending_piece: ChessPiece = board_state.piece_board[new_loc]
                if defending_piece is not None:
                    if defending_piece.type == "R" and defending_piece.is_white == piece.is_white and file == board.files - 1:
                        rook = defending_piece
                    break
                file += 1
            if rook is not None:
                #Filter move that causes check
                castleable = True
                move: ChessMove
                for move in board_state.black_moves:
                    if (move.new_position[0], move.new_position[1]) == (ro, fo + 2):
                        castleable = False
                        break
                if castleable:
                    moves.append(ChessMove(piece, (ro, fo + 2), castle=True, castle_rook_move=ChessMove(rook, (ro, fo + 1))))
    if castle_check_queen is False:
        #Make sure castling is available
        if board_state.castle_avail.find('Q' if piece.is_white else 'q') >= 0:
            #Make sure file is open
            rook: ChessPiece = None
            file = fo - 1
            while file >= 0:
                new_loc = ro * board.files + file
                defending_piece: ChessPiece = board_state.piece_board[new_loc]
                if defending_piece is not None:
                    if defending_piece.type == "R" and defending_piece.is_white == piece.is_white and file == 0:
                        rook = defending_piece
                    break
                file -= 1
            if rook is not None:
                #Filter move that causes check
                castleable = True
                move: ChessMove
                for move in board_state.black_moves:
                    if (move.new_position[0], move.new_position[1]) == (ro, fo - 2):
                        castleable = False
                        break
                if castleable:
                    moves.append(ChessMove(piece, (ro, fo - 2), castle=True, castle_rook_move=ChessMove(rook, (ro, fo - 1))))
    return moves

def _get_king_moves(piece, board, board_state) -> tuple[list, list]:
    """Get all moves that the piece can take including captures.

        Returns: List of moves and list of attacks.
    """
    moves = []
    attacks = []
    ro, fo = piece.position[0] - 1, piece.position[1] - 1
    castle_check_king = False
    castle_check_queen = False
    for ri in range(3):
        for fi in range(3):
            #Filter piece
            if ri == 1 and fi == 1:
                continue
            #Filter out of bounds
            r, f = ro + ri, fo + fi
            if r < 0 or r >= board.ranks or f < 0 or f >= board.files:
                continue
            #Add moves and attacks
            new_loc = r * board.files + f
            defending_piece: ChessPiece = board_state.piece_board[new_loc]
            if defending_piece is None:
                new_move = ChessMove(piece, (r, f))
                if board.check_move_for_check(new_move, board_state) is False:
                    moves.append(new_move)
                elif ri == 1 and fi == 0:
                    castle_check_queen = False
                elif ri == 1 and fi == 2:
                    castle_check_king = False
            elif defending_piece.is_white != piece.is_white:
                new_move = ChessMove(piece, (r, f))
                if board.check_move_for_check(new_move, board_state) is False:
                    moves.append(new_move)
                    attacks.append(new_move)
                elif ri == 1 and fi == 0:
                    castle_check_queen = False
                elif ri == 1 and fi == 2:
                    castle_check_king = False
    if board_state.check_status is None:
        moves = moves + _get_king_castle(piece, board, board_state, castle_check_king, castle_check_queen)
    return moves, attacks

def _get_pawn_check(piece, board, piece_board: list, king_positions: list) -> bool:
    """Calculates if this piece can attack the king with the passed board_state efficiently.

        Returns: True if the piece can take the other player's king.
    """
    king_r, king_f = king_positions[1] if piece.is_white else  king_positions[0]
    r_diff = -1 if piece.is_white else 1
    if king_r == piece.position[0] + r_diff:
        if king_f == piece.position[1] + 1 or king_f == piece.position[1] - 1:
            return True
    return False

def _get_knight_check(piece, board, piece_board: list, king_positions: list) -> bool:
    """Calculates if this piece can attack the king with the passed board_state efficiently.

        Returns: True if the piece can take the other player's king.
    """
    king_r, king_f = king_positions[1] if piece.is_white else  king_positions[0]
    if abs(king_r - piece.position[0]) <= 2:
        if abs(king_f - piece.position[1]) <= 2:
            #Top or bottom
            r1, r2 = 1, 2
            if king_r < piece.position[0]:
                r1, r2 = -1, -2
            #Left or right
            f1, f2 = 2, 1
            if king_f < piece.position[1]:
                f1, f2 = -2, -1
            if (piece.position[0] + r1, piece.position[1] + f1) == (king_r, king_f) or (piece.position[0] + r2, piece.position[1] + f2) == (king_r, king_f):
                return True
    return False

def _get_bishop_check(piece, board, piece_board: list, king_positions: list) -> bool:
    """Calculates if this piece can attack the king with the passed board_state efficiently.

        Returns: True if the piece can take the other player's king.
    """
    king_r, king_f = king_positions[1] if piece.is_white else  king_positions[0]
    r_d = 1 if king_r > piece.position[0] else -1
    f_d = 1 if king_f > piece.position[1] else -1
    rank_i, file_i = piece.position[0] + r_d, piece.position[1] + f_d
    while rank_i >= 0 and rank_i < board.ranks and file_i >= 0 and file_i < board.files:
        #If Piece Blocked
        new_loc = rank_i * board.files + file_i
        defending_piece: ChessPiece = piece_board[new_loc]
        if defending_piece is not None:
            if (rank_i, file_i) == (king_r, king_f):
                return True
            else:
                return False
        rank_i, file_i = rank_i + r_d, file_i + f_d
    return False

def _get_rook_check(piece, board, piece_board: list, king_positions: list) -> bool:
    """Calculates if this piece can attack the king with the passed board_state efficiently.

        Returns: True if the piece can take the other player's king.
    """
    king_r, king_f = king_positions[1] if piece.is_white else king_positions[0]

    #Get Rook Direction
    r_d, f_d = 1, 0
    if king_r < piece.position[0]:
        r_d, f_d = -1, 0
    elif king_f != piece.position[1]:
        if king_f < piece.position[1]:
            r_d, f_d = 0, -1
        else:
            r_d, f_d = 0, 1

    #Find King in valid moves
    rank_i, file_i = piece.position[0] + r_d, piece.position[1] + f_d
    while rank_i >= 0 and rank_i < board.ranks and file_i >= 0 and file_i < board.files:
        #If Piece Blocked
        new_loc = rank_i * board.files + file_i
        defending_piece: ChessPiece = piece_board[new_loc]
        if defending_piece is not None:
            if (rank_i, file_i) == (king_r, king_f):
                return True
            else:
                return False
        rank_i, file_i = rank_i + r_d, file_i + f_d
    return False

def _get_queen_check(piece, board, piece_board: list, king_positions: list) -> bool:
    """Calculates if this piece can attack the king with the passed board_state efficiently.

        Returns: True if the piece can take the other player's king.
    """
    king_r, king_f = king_positions[1] if piece.is_white else  king_positions[0]
    #If along a rooks path
    if king_r == piece.position[0] or king_f == piece.position[1]:
        return _get_rook_check(piece, board, piece_board, king_positions)
    else:
        return _get_bishop_check(piece, board, piece_board, king_positions)
    
def _get_king_check(piece, board, piece_board: list, king_positions: list) -> bool:
    """Calculates if this piece can attack the king with the passed board_state efficiently.

        Returns: True if the piece can take the other player's king.
    """
    king_r, king_f = king_positions[1] if piece.is_white else  king_positions[0]
    if abs(king_r - piece.position[0]) <= 1 and abs(king_f - piece.position[1]) <= 1:
        return True
    return False

def set_type_functions(piece_type: str = None) -> tuple[Callable, Callable]:
    """Checks they type of piece located at (rank_i_old, file_i_old) and determines which types of move check function to return.

        Returns: Check Moves Function specific to the type of piece at (rank_i_old, file_i_old)
    """
    p_str = piece_type if piece_type is not None else "P"
    move_function, check_function = _get_pawn_moves, _get_pawn_check
    if p_str == "P":
        return move_function, check_function 
    elif p_str == "N":
        move_function, check_function  = _get_knight_moves, _get_knight_check
    elif p_str == "B":
        move_function, check_function  = _get_bishop_moves, _get_bishop_check
    elif p_str == "R":
        move_function, check_function  = _get_rook_moves, _get_rook_check
    elif p_str == "Q":
        move_function, check_function  = _get_queen_moves, _get_queen_check
    elif p_str == "K":
        move_function, check_function  = _get_king_moves, _get_king_check
    return move_function, check_function


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
        self.move_function, self.check_function = set_type_functions(type)

    def calc_moves_attacks(self, board, board_state) -> "ChessPiece":
        """Calculates all moves and all attacks the piece is able to make.

            Returns piece for chaining
        """
        self.moves, self.attacks = self.move_function(self, board, board_state)
        return self
    
    def get_piece_check(self, board, piece_board: list, king_positions: list) -> bool:
        """Calculates if the piece is able to take the king.

            Returns True if the piece can take the king in the passed board_state, False if otherwise.
        """
        return self.check_function(self, board, piece_board, king_positions)
    