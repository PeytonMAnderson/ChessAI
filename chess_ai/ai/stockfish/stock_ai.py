import chess
import chess.engine
import time

from ..base_ai import BaseAI
from ...chess_logic.chess_move import ChessMove

class StockFishAI(BaseAI):
    def __init__(self, is_white: bool, *args, **kwargs):
        super().__init__(is_white, *args, **kwargs)
        self.engine = chess.engine.SimpleEngine.popen_uci(r'.\chess_ai\ai\stockfish\stockfish\stockfish-windows-2022-x86-64-avx2.exe')
        
    def execute_turn(self, board: list, env):
        start = time.time()
        chess_board = chess.Board(env.chess.board.board_to_fen())
        result = self.engine.play(chess_board, chess.engine.Limit(time=0.1))
        san = chess_board.san(result.move)
        chess_board.push(result.move)
        new_fen = chess_board.fen()
        env.chess.board.fen_to_board(new_fen)
        env.chess.move_extra(env, move_str=san)
        end = time.time()
        e = round((end-start)*1000, 3)
        print(f"DONE! Found Best Move: {san} in {e} ms")