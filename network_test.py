from chess_ai.ai.policy_network.create_data import create_data, get_data, cli_board

from chess_ai.chess_logic import *
from chess_ai.ai import *

OUTPUT_FILE_PATH = "./chess_ai/ai/policy_network/train_data/train.json"

score = ChessScore({"PAWN": 1, "KNIGHT": 3, "BISHOP": 3, "ROOK": 4, "QUEEN": 9, "KING": 10, "CHECK": 0, "CHECKMATE": 1000})
board = ChessBoard(ChessUtils({"NONE": 0, "PAWN": 1, "KNIGHT": 2, "BISHOP": 3, "ROOK": 4, "QUEEN": 5, "KING": 6, "WHITE": 1, "BLACK": 2}))
ai = RandomAI()

board.fen_to_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0")
score.calc_position_bias(board)

create_data(board, score, ai, 10_000, 50, OUTPUT_FILE_PATH)
# data = get_data()
# cli = cli_board(board, data[999].get('boards'))
# print(cli)