import time

from ..chess_logic import *

class BaseAI:
    def __init__(self, score: ChessScore, *args, **kwargs):
        self.score = score

    def get_move(self, board: ChessBoard, board_state: ChessBoardState) -> ChessMove:
        raise TypeError("Not Implemented Yet.")
    
    def execute_turn(self, board: ChessBoard) -> None:
        start = time.time()
        move = self.get_move(board, board.state)
        if move is not None:
            board.move_piece(move, board.state)
            end = time.time()
            e = round((end-start)*1000, 3)
            print(f"DONE! Found Best Move: {board.move_to_uci(move)} in {e} ms")
            return True
        return False