
import numpy as np

from chess_ai.chess_logic.chess_utils import ChessUtils
from chess_ai.chess_logic.chess_board import ChessBoardState, ChessBoard
from chess_ai.chess_logic.chess_piece import ChessPiece
from chess_ai.chess_logic.chess_move import ChessMove
from chess_ai.chess_logic.chess_score import ChessScore 
from chess_ai.ai.neural_network.gym_env.envs.chess_env import ChessEnv

board = ChessBoard(ChessUtils({"NONE": 0, "PAWN": 1, "KNIGHT": 2, "BISHOP": 3, "ROOK": 4, "QUEEN": 5, "KING": 6, "WHITE": 1, "BLACK": 2}))
scores = ChessScore({"PAWN": 1, "KNIGHT": 3, "BISHOP": 3, "ROOK": 4, "QUEEN": 9, "KING": 10, "CHECK": 0, "CHECKMATE": 1000})
board.fen_to_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0")
ce = ChessEnv(board, scores, 50)

action_array = np.zeros_like(ce.action)
action_array[6*board.files + 0] = 1
action_array[(board.files * board.ranks) + 3*board.files + 0] = 1

observation, reward, terminated, info = ce.step(action_array)


print(f"{reward, terminated, info}")