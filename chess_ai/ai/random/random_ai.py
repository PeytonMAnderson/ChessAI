
import random
from ..base_ai import BaseAI
from ...chess_logic.chess_board import ChessBoard, ChessBoardState
from ...chess_logic.chess_move import ChessMove

class RandomAI(BaseAI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_move(self, board: ChessBoard, board_state: ChessBoardState, env = None) -> ChessMove:
        if board_state.whites_turn:
            move_count = len(board_state.white_moves)
            random_move = random.randint(0, move_count-1)
            return board_state.white_moves[random_move]
        else:
            move_count = len(board_state.black_moves)
            random_move = random.randint(0, move_count-1)
            return board_state.black_moves[random_move]

    def execute_turn(self, board: ChessBoard, env = None) -> None:
        if board.state.whites_turn:
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