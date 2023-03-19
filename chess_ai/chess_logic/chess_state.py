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

    def update_from_move_dict(self, new_move: dict) -> "ChessState":
        self.whites_turn = new_move['whites_turn']
        self.castle_avail = new_move['castle_avail']
        self.en_passant = new_move['en_passant']
        self.half_move = new_move['half_move']
        self.full_move = new_move['full_move']
        return self