
import yaml
import tensorflow as tf
import numpy as np

from chess_ai.ai.policy_network.data import create_data, calc_board_arrays, de_normalize, normalize
from chess_ai.chess_logic import *
from chess_ai.ai.random.random_ai import RandomAI

CONFIG_FILE = "./chess_config.yaml"
TRAIN_DATA_FILE_PATH = "./chess_ai/ai/policy_network/train_data/train.json"
MODEL_FILE_PATH = './chess_ai/ai/policy_network/models/policy_network.model'
TEST_STRING = "rnbq1rk1/pppp1ppp/5n2/4p3/2B1P3/2PP1N2/P4PPP/RNBQK2R w KQ - 1 6"
TEST_STRING2 = "r1bqkbnr/pppppppp/n7/8/8/P7/1PPPPPPP/RNBQKBNR w KQkq - 2 2"

def get_from_yaml(yaml_path: str):
    with open(yaml_path, "r") as f:
        yaml_settings = yaml.safe_load(f)
        settings = yaml_settings['CHESS']
        settings_list = [
            settings['BOARD_RANKS'],
            settings['BOARD_FILES'],
            settings['MAX_HALF_MOVES'],
            settings['PIECE_VALUES'],
            settings['PIECE_SCORES'],
            settings['BOARD']
        ]
        return tuple(settings_list)

def main():
    #Set Up Board
    ranks, files, half_moves, piece_values, piece_scores, board_fen = get_from_yaml(CONFIG_FILE)
    board = ChessBoard(ChessUtils(piece_values), ranks, files)
    score = ChessScore(piece_scores)
    board.fen_to_board(board_fen)
    score.calc_position_bias(board)
    score.set_max_score(board, board.state)

    #Load Model
    model: tf.keras.Sequential = tf.keras.models.load_model(MODEL_FILE_PATH)

    #Get Scores
    board.fen_to_board(TEST_STRING2)
    board_arrays = np.array([np.array(calc_board_arrays(board, board.state))])
    real_score = score.calc_score(board, board.state)
    pred_score = model.predict(board_arrays)
    print(f"Predicted: {de_normalize(pred_score[0][0], score)}, Actual Score: {real_score}")


if __name__ == "__main__":
    main()