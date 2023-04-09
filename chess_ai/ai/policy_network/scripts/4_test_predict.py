
import yaml
import tensorflow as tf
import numpy as np

from chess_ai.ai.policy_network.data import create_data, calc_board_arrays, de_normalize, normalize
from chess_ai.chess_logic import *
from chess_ai.ai.random.random_ai import RandomAI

CONFIG_FILE = "./chess_config.yaml"
TRAIN_DATA_FILE_PATH = "./chess_ai/ai/policy_network/train_data/train.json"
MODEL_FILE_PATH = './chess_ai/ai/policy_network/models'
MODEL_NAME = 'policy_network2.model'
TEST_STRING = "rnbq1rk1/pppp1ppp/5n2/4p3/2B1P3/2PP1N2/P4PPP/RNBQK2R w KQ - 1 6"
TEST_STRING2 = "2kr3r/p1ppqpb1/bn2Qnp1/3PN3/1p2P3/2N5/PPPBBPPP/R3K2R b KQ - 3 2"

TOLERANCE = 0.1

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
    
def _get_boards_arrays(board: ChessBoard, board_state: ChessBoardState, score: ChessScore, move_list: list[ChessMove]) -> list:
    board_arrays_array = []
    acutal_scores = []
    move: ChessMove
    for move in move_list:
        new_board_state = board.move_piece(move, board_state, True)
        board_arrays_array.append(calc_board_arrays(board, new_board_state))
        acutal_scores.append(score.calc_score(board, new_board_state))
    return np.array(board_arrays_array), acutal_scores

def main():
    #Set Up Board
    ranks, files, half_moves, piece_values, piece_scores, board_fen = get_from_yaml(CONFIG_FILE)
    board = ChessBoard(ChessUtils(piece_values), ranks, files)
    score = ChessScore(piece_scores)
    board.fen_to_board(board_fen)
    score.calc_position_bias(board)
    score.set_max_score(board, board.state)

    #Load Model
    model: tf.keras.Sequential = tf.keras.models.load_model(MODEL_FILE_PATH + "/" + MODEL_NAME)

    #Get Boards and Scores
    board.fen_to_board(TEST_STRING2)
    move: ChessMove
    moves_list = board.state.white_moves if board.state.whites_turn else board.state.black_moves
    board_arrays, actual_scores = _get_boards_arrays(board, board.state, score, moves_list)
    new_pred_scores = model.predict(board_arrays)

    count = 0
    tolerables = 0
    differences = 0
    for scores in new_pred_scores:
        this_actual_score = actual_scores[count]
        this_pred_score = round(de_normalize(scores[0], score), 5)
        diff = round(abs(this_actual_score - this_pred_score), 5)
        tolerable = True if diff < TOLERANCE else False
        if tolerable:
            tolerables += 1
        differences += diff
        print(f"Move: ({moves_list[count].piece.position} => {moves_list[count].new_position}) Predicted: {this_pred_score},\tActual Score: {this_actual_score},\tDiff: {diff}\tTolerable: {tolerable}")
        count += 1
    
    print(f"Predicted {count} moves with {tolerables} tolerable predictions.")
    print(f"Average Difference: {round(differences / count, 5)}")

if __name__ == "__main__":
    main()