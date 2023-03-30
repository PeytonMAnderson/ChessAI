
import numpy as np
import random

from chess_ai.chess_logic.chess_utils import ChessUtils
from chess_ai.chess_logic.chess_board import ChessBoardState, ChessBoard
from chess_ai.chess_logic.chess_piece import ChessPiece
from chess_ai.chess_logic.chess_move import ChessMove
from chess_ai.chess_logic.chess_score import ChessScore 
from chess_ai.ai.neural_network.gym_env.envs.chess_env import ChessEnv
from chess_ai.ai.random.random_ai import RandomAI

board = ChessBoard(ChessUtils({"NONE": 0, "PAWN": 1, "KNIGHT": 2, "BISHOP": 3, "ROOK": 4, "QUEEN": 5, "KING": 6, "WHITE": 1, "BLACK": 2}))
scores = ChessScore({"PAWN": 1, "KNIGHT": 3, "BISHOP": 3, "ROOK": 4, "QUEEN": 9, "KING": 10, "CHECK": 0, "CHECKMATE": 1000})
scores.set_max_score(board, board.state)
scores.calc_position_bias(board)

board.fen_to_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0")
ce = ChessEnv(board, scores, 50, RandomAI(False))

for i in range(1000):
    if len(ce.chess_board.state.white_moves) == 0:
        break
    move_i = random.randint(0, len(ce.chess_board.state.white_moves) - 1)
    move = ce.chess_board.state.white_moves[move_i]
    ce._set_act(move)
    observation, reward, terminated, info = ce.step(ce.action)
    print(f"{i}: {reward, terminated, info}")