
import random
from ..base_ai import BaseAI
from ...chess_logic.chess_board import ChessBoard
from ...chess_logic.chess_move import ChessMove

class RandomAI(BaseAI):
    def __init__(self, is_white: bool, *args, **kwargs):
        super().__init__(is_white, *args, **kwargs)

    def get_move(self, board: ChessBoard, env = None) -> ChessMove:
        if self.is_white:
            move_count = len(board.state.white_moves)
            random_move = random.randint(0, move_count-1)
            return board.state.white_moves[random_move]
        else:
            move_count = len(board.state.black_moves)
            random_move = random.randint(0, move_count-1)
            return board.state.black_moves[random_move]

    def execute_turn(self, board: ChessBoard, env = None) -> None:
        if self.is_white:
            move_count = len(board.state.white_moves)
            random_move = random.randint(0, move_count-1)
            if env is None:
                board.move_piece(board.state.white_moves[random_move], board.state)
            else:
                env.chess.move_piece(board.state.white_moves[random_move], env)
        else:
            move_count = len(board.state.black_moves)
            random_move = random.randint(0, move_count-1)
            if env is None:
                board.move_piece(board.state.black_moves[random_move], board.state)
            else:
                env.chess.move_piece(board.state.black_moves[random_move], env)