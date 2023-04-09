import chess
import chess.engine
import time

from ..base_ai import BaseAI
from ...chess_logic import *

class StockFishAI(BaseAI):
    def __init__(self, score:  ChessScore, time_limit: int = 0.1, *args, **kwargs):
        super().__init__(score, *args, **kwargs)
        self.engine = chess.engine.SimpleEngine.popen_uci(r'.\chess_ai\ai\stockfish\stockfish\stockfish-windows-2022-x86-64-avx2.exe')
        self.time_limit = time_limit

    def get_move(self, board: ChessBoard, board_state: ChessBoardState) -> ChessMove:
        chess_board = chess.Board(board.board_to_fen(board_state))
        result = self.engine.play(chess_board, chess.engine.Limit(self.time_limit))
        return board.uci_to_move(result.move.uci())