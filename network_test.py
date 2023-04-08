import tensorflow as tf
import numpy as np

from chess_ai.ai.policy_network.data import create_data, get_formated_data, cli_board, calc_board_arrays
from chess_ai.ai.policy_network.network import create_network

from chess_ai.chess_logic import *
from chess_ai.ai import *

OUTPUT_FILE_PATH = "./chess_ai/ai/policy_network/train_data/train.json"
TEST_STRING = "rnbq1rk1/pppp1ppp/5n2/4p3/2B1P3/2PP1N2/P4PPP/RNBQK2R w KQ - 1 6"

score = ChessScore({"PAWN": 1, "KNIGHT": 3, "BISHOP": 3, "ROOK": 4, "QUEEN": 9, "KING": 10, "CHECK": 0, "CHECKMATE": 1000})
board = ChessBoard(ChessUtils({"NONE": 0, "PAWN": 1, "KNIGHT": 2, "BISHOP": 3, "ROOK": 4, "QUEEN": 5, "KING": 6, "WHITE": 1, "BLACK": 2}))
ai = RandomAI()

board.fen_to_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0")
score.calc_position_bias(board)
score.set_max_score(board, board.state)

create_data(board, score, ai, 1_000, 50, OUTPUT_FILE_PATH)
x_train, y_train = get_formated_data(OUTPUT_FILE_PATH)
# cli = cli_board(board, data[999].get('boards'))
# print(cli)
# print(x_train[0])

board.fen_to_board(TEST_STRING)
board_arrays = calc_board_arrays(board, board.state)
board_arrays = np.array(board_arrays)
print(board_arrays)
print(board_arrays.shape)

model = create_network(x_train[0], board.ranks, board.files, 32, 4, 64)
model.compile(optimizer=tf.keras.optimizers.Adam(5e-4), loss='mean_squared_error')
model.summary()
model.fit(x_train, y_train, batch_size=2048, epochs=1000, verbose=1, validation_split=0.1, callbacks=[
    tf.keras.callbacks.ReduceLROnPlateau(monitor='loss', patience=10),
    tf.keras.callbacks.EarlyStopping(monitor='loss', patience=15)
])


#(-1000, 1000)
score_value  = score.calc_score(board, board.state)
#(-0.5, 0.5)
score_norm = score_value / (score.score_max_checkmate * 2)
#(0, 1)
score_norm_pos = score_norm + 0.5

prediction = model.predict(board_arrays)
# print(f"{score_norm_pos}, {prediction}")
