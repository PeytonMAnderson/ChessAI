from orjson import dumps, loads
import numpy as np

from ...chess_logic import *
from ..base_ai import BaseAI

OUTPUT_FILE_PATH = "./chess_ai/ai/policy_network/train_data/train.json"

def calc_piece_array(board: ChessBoard, board_state: ChessBoardState, is_white: bool, piece_type: str) -> list:
    piece_board = [0] * board.ranks * board.files
    for rank in range(board.ranks):
        for file in range(board.files):
            piece: ChessPiece = board_state.piece_board[rank * board.files + file]
            if piece is None:
                continue
            if piece.is_white != is_white:
                continue
            if piece.type == piece_type:
                piece_board[rank * board.files + file] = 1
    return piece_board

def calc_current_positions(board: ChessBoard, board_state: ChessBoardState) -> list:
    pos_list = [0] * board.ranks * board.files
    for rank in range(board.ranks):
        for file in range(board.files):
            piece: ChessPiece = board_state.piece_board[rank * board.files + file]
            if piece is None:
                continue
            if board_state.whites_turn and piece.is_white:
                pos_list[rank * board.files + file] = 1
            elif not board_state.whites_turn and not piece.is_white:
                pos_list[rank * board.files + file] = 1
    return pos_list

def calc_legal_moves(board: ChessBoard, board_state: ChessBoardState) -> list:
    legal_moves = [0] * board.ranks * board.files
    moves_array = board_state.white_moves if board_state.whites_turn else board_state.black_moves
    move: ChessMove
    for move in moves_array:
        r, f = move.new_position
        legal_moves[r * board.files + f] = 1
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

def calc_board_score(board: ChessBoard, board_state: ChessBoardState, score: ChessScore) -> float:
    return score.calc_score(board, board_state)

def generate_boards(board: ChessBoard, score: ChessScore, ai: BaseAI, n_boards: int, max_half_moves: int) -> list:
    boards = []
    board_count = 0
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
            board_score = calc_board_score(board, new_board_state, score)
            boards.append({"boards": board_array, "score": board_score})
            board_count += 1
        game_count += 1
        print(f"Finished Game {game_count}: Current board count: {board_count}.")
    print(f"Finished with {board_count} boards, from {game_count} games.")
    return boards

def create_data(board: ChessBoard, 
                score: ChessScore, 
                ai: BaseAI, 
                n_boards: int = 1_000, 
                max_half_moves: int = 50, 
                file_path: str = OUTPUT_FILE_PATH
    ) -> None:
    boards = generate_boards(board, score, ai, n_boards,  max_half_moves)
    with open(file_path, 'wb') as f:
        f.write(dumps(boards, option=0))

def get_data(file_path: str = OUTPUT_FILE_PATH) -> list:
    with open(file_path, 'rb') as f:
        boards = loads(f.read())
    return boards

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



