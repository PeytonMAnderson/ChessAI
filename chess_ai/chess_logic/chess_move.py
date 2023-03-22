

class ChessMove:
    def __init__(self, 
                 piece, 
                 new_position: tuple, 
                 castle: bool = False, 
                 en_passant: bool = False, 
                 castle_rook_move = None,
                 en_passant_pawn = None,
    *args, **kwargs) -> None:
        
        self.piece = piece
        self.new_position = new_position
        self.castle = castle
        self.en_passant = en_passant
        self.castle_rook_move = castle_rook_move
        self.en_passant_pawn = en_passant_pawn
