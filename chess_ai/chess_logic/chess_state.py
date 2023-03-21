class ChessState:
    def __init__(self, 
                whites_turn: bool = True,
                check_status: int | None = None,
                check_status_str: str = "None",
                castle_avail: str = 'KQkq',
                en_passant: str = '-',
                half_move: int = 0,
                full_move: int = 1,
                max_half_moves: int = 0,             
        *args, **kwargs) -> None:
        self.whites_turn = whites_turn
        self.check_status_str = check_status_str
        self.check_status = check_status
        self.castle_avail = castle_avail
        self.en_passant = en_passant
        self.half_move = half_move
        self.full_move = full_move
        self.last_move_str = "None"
        self.last_move_tuple = None
        self.game_ended = False
        self.max_half_moves = max_half_moves

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
    
    def calc_game_ended(self) -> "ChessState":
        if int(self.half_move) >= self.max_half_moves:
            self.game_ended = True
