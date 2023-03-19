class ChessState:
    def __init__(self, 
                whites_turn: bool = True,
                check_status: str = 'None',
                castle_avail: str = 'KQkq',
                en_passant: str = '-',
                half_move: int = 0,
                full_move: int = 1,             
        *args, **kwargs) -> None:
        self.whites_turn = whites_turn
        self.check_status = check_status
        self.castle_avail = castle_avail
        self.en_passant = en_passant
        self.half_move = half_move
        self.full_move = full_move
        self.last_move = None

    def update_from_move_dict(self, new_move: dict) -> "ChessState":
        self.whites_turn = new_move['whites_turn']
        self.castle_avail = new_move['castle_avail']
        self.en_passant = new_move['en_passant']
        self.half_move = new_move['half_move']
        self.full_move = new_move['full_move']
        return self
    
    def update_from_fen_list(self, new_fen: list) -> "ChessState":
        """list[ Board, Turn, Castling, enpassant, half_move, full_move ]
        """
        self.whites_turn = new_fen[1]
        self.castle_avail = new_fen[2]
        self.en_passant = new_fen[3]
        self.half_move = new_fen[4]
        self.full_move = new_fen[5]
        return self