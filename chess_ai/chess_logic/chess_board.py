

class ChessBoard:
    def __init__(self, board: list = None, board_ranks: int = 8, board_files: int = 8, piece_numbers: dict = None, *args, **kargs) -> None:
        self.board = board
        self.ranks = board_ranks
        self.files = board_files
        self.piece_numbers = piece_numbers

    def reset(self, board: list = None) -> "ChessBoard":
        if board is None:
            self.board = [0] * self.ranks * self.files
        else:
            self.board = board
        return self
    
    def get_piece_position(self, piece_value: int) -> tuple | None:
        """Get the piece's rank and file by checking the board in the parameters.

            Returns: tuple[rank_i, file_i] of the piece location. None if piece is not found.
        """
        rank_i = 0
        file_i = 0
        for piece in self.board:
            if piece == piece_value:
                return rank_i, file_i
            if file_i >= self.board.files - 1:
                rank_i += 1
                file_i = 0
            else:
                file_i += 1
        return None
    


    