
from .chess_utils import convert_board_to_fen, get_move_str
from .chess_check import check_for_check, check_move_cause_check
from .chess_utils import get_piece_value
from .chess_base_moves import *
from .chess_check import check_all_available_moves

def filter_moves(rank_i_old: int, file_i_old: int, move_list: list, env):
    filtered_moves = []
    for new_r, new_f in move_list:
        if check_move_cause_check(rank_i_old, file_i_old, new_r, new_f, env) is False:
            filtered_moves.append((new_r, new_f))
    return filtered_moves


def get_valid_moves(rank_i_old: int, file_i_old: int, env):
    piece_function = get_piece_type_function(rank_i_old, file_i_old, env.chess.board, env)
    if piece_function is not None:
        moves = piece_function(rank_i_old, file_i_old, env.chess.board, env)
        if moves is not None:
            return filter_moves(rank_i_old, file_i_old, moves, env)
        print("WARNING: Moves does not exist.")
    else:
        print("WARNING: Piece function does not exist.")
    return []

def move_piece(rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, env):
    board_position_old = rank_i_old * env.chess.board_files + file_i_old
    board_position_new = rank_i_new * env.chess.board_files + file_i_new

    if board_position_old < len(env.chess.board) and board_position_new < len(env.chess.board):
        
        #Get Move String
        new_move = get_move_str(rank_i_old, file_i_old, rank_i_new, file_i_new, env)

        #Update Piece on board
        env.chess.board[board_position_new] = env.chess.board[board_position_old]
        env.chess.board[board_position_old] = 0

        #Update Turn
        env.chess.whites_turn = False if env.chess.whites_turn else True

        #Get New FEN String
        new_board = convert_board_to_fen(env.chess.board, env.chess.board_files, env.chess.board_ranks, env.chess.piece_numbers, env)

        print(f"New Move: {new_move}")
        print(f"New Board: {new_board}")
        white_king_value = get_piece_value('K', env.chess.piece_numbers)
        black_king_value = get_piece_value('k', env.chess.piece_numbers)
        white_in_check = check_for_check(white_king_value, env.chess.board, env)
        black_in_check = check_for_check(black_king_value, env.chess.board, env)

        #If current position in history is less than the present and new move, remove all updates after history_position and update from there
        if len(env.chess.history) - 1 > env.chess.history_position:
            while len(env.chess.history) - 1 > env.chess.history_position:
                env.chess.history.pop()
        env.chess.history.append((new_move, new_board))
        env.chess.history_position = len(env.chess.history) - 1