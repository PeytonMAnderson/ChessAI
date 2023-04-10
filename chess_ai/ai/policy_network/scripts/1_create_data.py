
import yaml

from chess_ai.ai.policy_network.data import create_data
from chess_ai.chess_logic import *
from chess_ai.ai.random.random_ai import RandomAI

CONFIG_FILE = "./chess_config.yaml"
TRAIN_DATA_FILE_PATH = "./chess_ai/ai/policy_network/train_data/train.json"
N_BOARDS = 1_000
DEPTH = 2
RESET = True

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
    random_ai = RandomAI(score)

    #Create Data
    create_data(board, score, random_ai, N_BOARDS, half_moves, TRAIN_DATA_FILE_PATH, DEPTH, RESET)

if __name__ == "__main__":
    main()