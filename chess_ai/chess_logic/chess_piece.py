
from typing import Callable

from .chess_move import ChessMove
from .chess_board import ChessBoard

class ChessPiece:
    def __init__(self, 
                 value: int = 0, 
                 type: str = "", 
                 is_white: bool = None, 
                 position: tuple = (0, 0), 
                 flags: list = [], 
    *args, **kwargs) -> None:
        self.value = value
        self.type = type
        self.is_white = is_white
        self.position = position
        self.flags = flags
        move_function, check_function = self._get_type_functions(type)
        self.move_function = move_function
        self.check_function = check_function
        self.moves: list[ChessMove]
        self.attacks = list[ChessMove]

    def _get_pawn_moves(self, board: ChessBoard) -> tuple[list, list]:
        """Get all moves that the piece can take including captures.

            Returns: List of moves and list of attacks.
        """
        moves = []
        attacks = []
        rank_i_old, file_i_old = self.position
        rank_diff = -1 if self.is_white else 1

        #enpassant
        e_r, e_f = None, None
        if len(board.en_passant) == 2:
            e_r = board.utils.get_number_from_rank(board.en_passant[1], board.ranks)
            e_f = board.utils.get_number_from_file(board.en_passant[0])

        #Stay bounds
        if rank_i_old == 0 or rank_i_old == board.ranks - 1:
            return moves, attacks

        #Get basic moves
        new_loc = (rank_i_old + rank_diff) * board.files + file_i_old
        if board.piece_board[new_loc] is None:
            new_move = ChessMove(self, (rank_i_old + rank_diff, file_i_old))
            if board.check_move_for_check(new_move) is False:
                moves.append(new_move)
        if len(moves) == 1:
            if rank_i_old == 1 or rank_i_old == board.ranks - 2:
                new_loc = (rank_i_old + rank_diff * 2) * board.files + file_i_old
                if board.piece_board[new_loc] is None:
                    new_move = ChessMove(self, (rank_i_old + rank_diff * 2, file_i_old))
                    if board.check_move_for_check(new_move) is False:
                        moves.append(new_move)

        #Get attack left
        if file_i_old - 1 >= 0:
            defending_piece: ChessPiece = board.piece_board[(rank_i_old + rank_diff) * board.files + file_i_old - 1]

            #Check if can en passant
            can_en_passant = False
            if e_r is not None and e_f is not None:
                if (e_r, e_f) == (rank_i_old + rank_diff, file_i_old - 1):
                    if (e_r == 2 and self.is_white) or (e_r == board.ranks-3 and not self.is_white):
                        can_en_passant = True

            #Check if attackable
            if defending_piece is not None and defending_piece.is_white != self.is_white:
                new_move = ChessMove(self, (rank_i_old + rank_diff, file_i_old - 1))
                if board.check_move_for_check(new_move) is False:
                    moves.append(new_move)
                    attacks.append(new_move)
            elif can_en_passant:
                en_passant_piece: ChessPiece = board.piece_board[(rank_i_old) * board.files + file_i_old - 1]
                new_move = ChessMove(self, (rank_i_old + rank_diff, file_i_old - 1), en_passant=True, en_passant_pawn=en_passant_piece)                
                if board.check_move_for_check(new_move) is False:
                    moves.append(new_move)
                    attacks.append(new_move)

        #Get attack right
        if file_i_old + 1 < board.files:
            defending_piece: ChessPiece = board.piece_board[(rank_i_old + rank_diff) * board.files + file_i_old + 1]

            #Check if can en passant
            can_en_passant = False
            if e_r is not None and e_f is not None:
                if (e_r, e_f) == (rank_i_old + rank_diff, file_i_old - 1):
                    if (e_r == 2 and self.is_white) or (e_r == board.ranks-3 and not self.is_white):
                        can_en_passant = True

            #Check if attackable
            if defending_piece is not None and defending_piece.is_white != self.is_white:
                new_move = ChessMove(self, (rank_i_old + rank_diff, file_i_old + 1))
                if board.check_move_for_check(new_move) is False:
                    moves.append(new_move)
                    attacks.append(new_move)
            elif can_en_passant:
                en_passant_piece: ChessPiece = board.piece_board[(rank_i_old) * board.files + file_i_old + 1]  
                new_move = ChessMove(self, (rank_i_old + rank_diff, file_i_old + 1), en_passant=True, en_passant_pawn=en_passant_piece)             
                if board.check_move_for_check(new_move) is False:
                    moves.append(new_move)
                    attacks.append(new_move)
        return moves, attacks

    def _get_knight_moves(self, board) -> tuple[list, list]:
        """Get all moves that the piece can take including captures.

            Returns: List of moves and list of attacks.
        """
        moves = []
        attacks = []
        rank_i_old, file_i_old = self.position

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
                new_move = ChessMove(self, (rank_i_old + r, file_i_old + f))
                if board.check_move_for_check(new_move) is False:
                    moves.append(new_move)
            elif defending_piece.is_white != self.is_white:
                new_move = ChessMove(self, (rank_i_old + r, file_i_old + f))
                if board.check_move_for_check(new_move) is False:
                    moves.append(new_move)
                    attacks.append(new_move)
        
        return moves, attacks

    def _get_bishop_moves(self, board) -> tuple[list, list]:
        """Get all moves that the piece can take including captures.

            Returns: List of moves and list of attacks.
        """
        moves = []
        attacks = []
        rank_i_old, file_i_old = self.position

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
                    new_move = ChessMove(self, (rank_i, file_i))
                    if board.check_move_for_check(new_move) is False:
                        moves.append(new_move)
                elif defending_piece.is_white != self.is_white:
                    new_move = ChessMove(self, (rank_i, file_i))
                    if board.check_move_for_check(new_move) is False:
                        moves.append(new_move)
                        attacks.append(new_move)
                    break
                rank_i + dr
                file_i + df
        return moves, attacks

    def _get_rook_moves(self, board) -> tuple[list, list]:
        """Get all moves that the piece can take including captures.

            Returns: List of moves and list of attacks.
        """
        moves = []
        attacks = []
        rank_i_old, file_i_old = self.position

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
                    new_move = ChessMove(self, (rank_i, file_i))
                    if board.check_move_for_check(new_move) is False:
                        moves.append(new_move)
                elif defending_piece.is_white != self.is_white:
                    new_move = ChessMove(self, (rank_i, file_i))
                    if board.check_move_for_check(new_move) is False:
                        moves.append(new_move)
                        attacks.append(new_move)
                    break
                rank_i + dr
                file_i + df

        return moves, attacks

    def _get_queen_moves(self, board) -> tuple[list, list]:
        """Get all moves that the piece can take including captures.

            Returns: List of moves and list of attacks.
        """
        moves, attacks = self._get_bishop_moves(board)
        moves_2, attacks_2 = self._get_bishop_moves(board)
        return moves + moves_2, attacks + attacks_2

    def _get_king_moves(self, board) -> tuple[list, list]:
        """Get all moves that the piece can take including captures.

            Returns: List of moves and list of attacks.
        """
        moves = []
        attacks = []
        rank_i_old, file_i_old = self.position
        ro, fo = rank_i_old - 1, file_i_old - 1
        castle_check_king = False
        castle_check_queen = False
        for ri in range(3):
            for fi in range(3):
                if ri == 1 and fi == 1:

                    #Filter move that causes check
                    for _, _, rf, ff in board.black_moves:
                        if (rf, ff) == (r, f):
                            castle_check_queen, castle_check_king = True
                r, f = ro + ri, fo + fi
                new_loc = r * board.files + f
                defending_piece: ChessPiece = board.piece_board[new_loc]

                #Filter move that causes check
                for _, _, rf, ff in board.black_moves:
                    if (rf, ff) == (r, f):
                        if r == self.position[0]:
                            #King side
                            if f > self.position[1]:
                                castle_check_king = True
                            else:
                                castle_check_queen = True
                #Add moves and attacks
                if defending_piece is None:
                    moves.append(ChessMove(self, (r, f)))
                elif defending_piece.is_white != self.is_white:
                    new_move = ChessMove(self, (r, f))
                    moves.append(new_move)
                    attacks.append(new_move)

        #Add Castling Moves
        if castle_check_king is False:

            #Make sure castling is available
            if board.castle_avail.find('K' if self.is_white else 'k') >= 0:

                #Make sure file is open
                open_to_rook = True
                file = fo + 1
                while file < board.files - 1:
                    new_loc = ro * board.files + file
                    defending_piece: ChessPiece = board.piece_board[new_loc]
                    if defending_piece is not None:
                        open_to_rook = False
                        break
                    file += 1
                if open_to_rook:

                    #Filter move that causes check
                    castleable = True
                    for _, _, rf, ff in board.black_moves:
                        if (rf, ff) == (ro, fo + 2):
                            castleable = False
                            break
                    if castleable:
                        new_loc = ro * board.files + file
                        rook: ChessPiece = board.piece_board[new_loc]
                        moves.append(ChessMove(self, (ro, fo + 2), castle=True, castle_rook_move=ChessMove(rook, (ro, fo + 1))))

        if castle_check_queen is False:

            #Make sure castling is available
            if board.castle_avail.find('Q' if self.is_white else 'q') >= 0:

                #Make sure file is open
                open_to_rook = True
                file = fo - 1
                while file > 0:
                    new_loc = ro * board.files + file
                    defending_piece: ChessPiece = board.piece_board[new_loc]
                    if defending_piece is not None:
                        open_to_rook = False
                        break
                    file -= 1
                if open_to_rook:

                    #Filter move that causes check
                    castleable = True
                    for _, _, rf, ff in board.black_moves:
                        if (rf, ff) == (ro, fo - 2):
                            castleable = False
                            break
                    if castleable:
                        new_loc = ro * board.files + file
                        rook: ChessPiece = board.piece_board[new_loc]
                        moves.append(ChessMove(self, (ro, fo - 2), castle=True, castle_rook_move=ChessMove(rook, (ro, fo - 1))))
        return moves, attacks

    def _get_pawn_check(self, piece_board: list, king_positions: list, board_dim: tuple[int, int]) -> bool:
        """Calculates if this piece can attack the king with the passed board efficiently.

            Returns: True if the piece can take the other player's king.
        """
        king_r, king_f = king_positions[1] if self.is_white else  king_positions[0]
        r_diff = -1 if self.is_white else 1
        if king_r == self.position[0] + r_diff:
            if king_f == self.position[1] + 1 or king_f == self.position[1] - 1:
                return True
        return False
    
    def _get_knight_check(self, piece_board: list, king_positions: list, board_dim: tuple[int, int]) -> bool:
        """Calculates if this piece can attack the king with the passed board efficiently.

            Returns: True if the piece can take the other player's king.
        """
        king_r, king_f = king_positions[1] if self.is_white else  king_positions[0]
        if abs(king_r - self.position[0]) <= 2:
            if abs(king_f - self.position[1]) <= 2:
                #Top or bottom
                r1, r2 = 1, 2
                if king_r < self.position[0]:
                    r1, r2 = -1, -2
                #Left or right
                f1, f2 = 2, 1
                if king_f < self.position[1]:
                    f1, r2 = -2, -1
                if (r1, f1) == (king_r, king_f) or (r2, f2) == (king_r, king_f):
                    return True
        return False
    
    def _get_bishop_check(self, piece_board: list, king_positions: list, board_dim: tuple[int, int]) -> bool:
        """Calculates if this piece can attack the king with the passed board efficiently.

            Returns: True if the piece can take the other player's king.
        """
        king_r, king_f = king_positions[1] if self.is_white else  king_positions[0]
        r_d = 1 if king_r > self.position[0] else -1
        f_d = 1 if king_f > self.position[1] else -1
        rank_i, file_i = self.position[0] + r_d, self.position[1] + f_d
        while rank_i >= 0 and rank_i < board_dim[0] and file_i >= 0 and file_i < board_dim[1]:
            #If Piece Blocked
            new_loc = rank_i * board_dim[1] + file_i
            defending_piece: ChessPiece = piece_board[new_loc]
            if defending_piece is not None:
                if (rank_i, file_i) == (king_r, king_f):
                    return True
                else:
                    return False
            rank_i, file_i = rank_i + r_d, file_i + f_d
        return False

    def _get_rook_check(self, piece_board: list, king_positions: list, board_dim: tuple[int, int]) -> bool:
        """Calculates if this piece can attack the king with the passed board efficiently.

            Returns: True if the piece can take the other player's king.
        """
        king_r, king_f = king_positions[1] if self.is_white else  king_positions[0]

        #Get Rook Direction
        r_d, f_d = 1, 0
        if king_r < self.position[0]:
            r_d, f_d = -1, 0
        elif king_f != self.position[1]:
            if king_r < self.position[1]:
                r_d, f_d = 0, -1
            else:
                r_d, f_d = 0, 1

        #Find King in valid moves
        rank_i, file_i = self.position[0] + r_d, self.position[1] + f_d
        while rank_i >= 0 and rank_i < board_dim[0] and file_i >= 0 and file_i < board_dim[1]:
            #If Piece Blocked
            new_loc = rank_i * board_dim[1] + file_i
            defending_piece: ChessPiece = piece_board[new_loc]
            if defending_piece is not None:
                if (rank_i, file_i) == (king_r, king_f):
                    return True
                else:
                    return False
            rank_i, file_i = rank_i + r_d, file_i + f_d
        return False
    
    def _get_queen_check(self, piece_board: list, king_positions: list, board_dim: tuple[int, int]) -> bool:
        """Calculates if this piece can attack the king with the passed board efficiently.

            Returns: True if the piece can take the other player's king.
        """
        king_r, king_f = king_positions[1] if self.is_white else  king_positions[0]

        #If along a rooks path
        if king_r == self.position[0] or king_f == self.position[1]:
            return self._get_rook_check(piece_board, king_positions)
        else:
            return self._get_bishop_check(piece_board, king_positions)
        
    def _get_king_check(self, piece_board: list, king_positions: list, board_dim: tuple[int, int]) -> bool:
        """Calculates if this piece can attack the king with the passed board efficiently.

            Returns: True if the piece can take the other player's king.
        """
        king_r, king_f = king_positions[1] if self.is_white else  king_positions[0]
        if abs(king_r - self.position[0]) <= 1 or abs(king_f - self.position[1]) <= 1:
            return True
        return False

    def _get_type_move_function(self, piece_type: str) -> Callable:
        """Checks they type of piece located at (rank_i_old, file_i_old) and determines which types of move check function to return.

            Returns: Check Moves Function specific to the type of piece at (rank_i_old, file_i_old)
        """
        move_function, check_function = self._get_pawn_moves, self._get_pawn_check
        if piece_type == "P":
            return move_function, check_function 
        elif piece_type == "N":
            move_function, check_function  = self._get_knight_moves, self._get_knight_check
        elif piece_type == "B":
            move_function, check_function  = self._get_bishop_moves, self._get_bishop_check
        elif piece_type == "R":
            move_function, check_function  = self._get_rook_moves, self._get_rook_check
        elif piece_type == "Q":
            move_function, check_function  = self._get_queen_moves, self._get_queen_check
        elif piece_type == "K":
            move_function, check_function  = self._get_king_moves, self._get_king_check
        return move_function, check_function 

    def calc_moves_attacks(self, board) -> "ChessPiece":
        """Calculates all moves and all attacks the piece is able to make.

            Returns self for chaining
        """
        self.moves, self.attacks = self.move_function(board)
    
    def get_piece_check(self, piece_board: list, king_positions: list, board_dim: tuple[int, int]) -> bool:
        """Calculates if the piece is able to take the king.

            Returns True if the piece can take the king in the passed board, False if otherwise.
        """
        return self.check_function(piece_board, king_positions, board_dim)
    