from orjson import dumps, loads
import numpy as np

from ...chess_logic import *
from ..base_ai import BaseAI
from ...minimax import MinimaxAlphaBeta

OUTPUT_FILE_PATH = "./chess_ai/ai/policy_network/train_data/train.json"
BIG_NUMBER = 1000000

def get_data(file_path: str = OUTPUT_FILE_PATH) -> list:
    with open(file_path, 'rb') as f:
        boards = loads(f.read())
    return boards

def calc_piece_array(board: ChessBoard, board_state: ChessBoardState, is_white: bool, piece_type: str) -> list:
    piece_board = [[0 for f in range(board.files)] for r in range(board.ranks)]
    for rank in range(board.ranks):
        for file in range(board.files):
            piece: ChessPiece = board_state.piece_board[rank * board.files + file]
            if piece is None:
                continue
            if piece.is_white != is_white:
                continue
            if piece.type == piece_type:
                piece_board[rank][file] = 1
    return piece_board

def calc_current_positions(board: ChessBoard, board_state: ChessBoardState) -> list:
    pos_list = [[0 for f in range(board.files)] for r in range(board.ranks)]
    for rank in range(board.ranks):
        for file in range(board.files):
            piece: ChessPiece = board_state.piece_board[rank * board.files + file]
            if piece is None:
                continue
            if board_state.whites_turn and piece.is_white:
                pos_list[rank][file] = 1
            elif not board_state.whites_turn and not piece.is_white:
                pos_list[rank][file] = 1
    return pos_list

def calc_legal_moves(board: ChessBoard, board_state: ChessBoardState) -> list:
    legal_moves = [[0 for f in range(board.files)] for r in range(board.ranks)]
    moves_array = board_state.white_moves if board_state.whites_turn else board_state.black_moves
    move: ChessMove
    for move in moves_array:
        r, f = move.new_position
        legal_moves[r][f] = 1
    return legal_moves

def calc_board_arrays(board: ChessBoard, board_state: ChessBoardState) -> list:
    board_arrays = []
    board_types = [
        "W_P",
        "W_N",
        "W_B",
        "W_R",
        "W_Q",
        "W_K",
        "B_P",
        "B_N",
        "B_B",
        "B_R",
        "B_Q",
        "B_K",
        "current_positions",
        "legal_moves"
    ]
    for board_str in board_types:
        str_array = board_str.split("_")
        is_white = True if str_array[0] == "W" else False
        piece_type = str_array[1]
        if board_str == "current_positions":
            board_arrays.append(calc_current_positions(board, board_state))
        elif board_str == "legal_moves":
            board_arrays.append(calc_legal_moves(board, board_state))
        else:
            board_arrays.append(calc_piece_array(board, board_state, is_white, piece_type))
    return board_arrays

def normalize(score_value: float, score: ChessScore) -> float:
    return (score_value / (score.score_max_checkmate * 2)) + 0.5

def de_normalize(score_value: float, score: ChessScore) -> float:
    return (score_value - 0.5) * (score.score_max_checkmate * 2)

def calc_board_score(board: ChessBoard, board_state: ChessBoardState, score: ChessScore, depth: int) -> float:
    #(-1000, 1000)
    score_value = 0
    if depth == -1:
        score_value = score.calc_score(board, board_state)
    else:
        minimax = MinimaxAlphaBeta(score)
        score_value, branches = minimax.minimax(board, board_state, depth=depth, track_move=False)
    #(-0.5, 0.5)
    score_norm = score_value / (score.score_max_checkmate * 2)
    #(0, 1)
    score_norm_pos = score_norm + 0.5
    return score_norm_pos

def generate_boards(board: ChessBoard, 
                    score: ChessScore, 
                    ai: BaseAI, 
                    n_boards: int, 
                    max_half_moves: int, 
                    depth: int, 
                    file_path: str,
                    starting_board: int = 0
) -> list:
    boards = []
    board_count = starting_board
    game_count = 0
    #Keep looping until n boards is filled
    while board_count < n_boards:
        #Keep looping until game is finished
        game_ended = False
        new_board_state = board.state
        while not game_ended and board_count < n_boards:
            move: ChessMove = ai.get_move(board, new_board_state)
            new_board_state = board.move_piece(move, new_board_state, True)
            if new_board_state.half_move >= max_half_moves:
                game_ended = True
            elif new_board_state.check_status is not None:
                if abs(new_board_state.check_status) == 2 or new_board_state.check_status == 0:
                    game_ended = True
            board_array = calc_board_arrays(board, new_board_state)
            board_score = calc_board_score(board, new_board_state, score, depth)
            board_dict = {"boards": board_array, "score": board_score}
            board_count += 1
            if depth > 1:
                print(f"\tBoard Created: {board_count}, Depth {depth}, Score: {board_score}")
                boards_json: list = get_data(file_path)
                boards_json.append(board_dict)
                with open(file_path, 'wb') as f:
                    f.write(dumps(boards_json, option=0))
            else:
                boards.append(board_dict)
        game_count += 1
        print(f"Finished Game {game_count}: Current board count: {board_count}.")
    print(f"Finished with {board_count} boards, from {game_count} games.")
    return boards

def create_data(board: ChessBoard, 
                score: ChessScore, 
                ai: BaseAI, 
                n_boards: int = 1_000, 
                max_half_moves: int = 50, 
                file_path: str = OUTPUT_FILE_PATH,
                depth: int = -1,
                reset: bool = False
    ) -> None:
    
    starting_board = 0
    if depth >= 0 and reset:
        print("Data Reset.")
        with open(file_path, 'wb') as f:
            f.write(dumps([], option=0))
    current_boards = get_data(file_path)
    if isinstance(current_boards, list):
        starting_board = len(current_boards)
    print(f"Generating Boards starting with board {starting_board}")
    boards = generate_boards(board, score, ai, n_boards,  max_half_moves, depth, file_path, starting_board)
    if depth == -1:
        with open(file_path, 'wb') as f:
            f.write(dumps(boards, option=0))

def get_formated_data(file_path: str = OUTPUT_FILE_PATH) -> tuple[np.ndarray, np.ndarray]:
    with open(file_path, 'rb') as f:
        boards = loads(f.read())
        x_train = []
        y_train = []
        for b in boards:
            score = b.get("score")
            bds = b.get("boards")
            x_train.append(bds)
            y_train.append(score)
    return np.array(x_train), np.array(y_train)

def cli_board(board: ChessBoard, board_lists: list) -> None:
    board_types = [
        "W_P",
        "W_N",
        "W_B",
        "W_R",
        "W_Q",
        "W_K",
        "B_P",
        "B_N",
        "B_B",
        "B_R",
        "B_Q",
        "B_K",
        "current_positions",
        "legal_moves"
    ]
    count = 0
    for b in board_lists:
        new_label = board_types[count]
        print(f"{new_label}: ")
        for r in range(board.ranks):
            new_rank = []
            rank_offset = r * board.files
            for f in range(board.files):
                new_rank.append(b[rank_offset + f])
            print(f"{new_rank}")
        count += 1



