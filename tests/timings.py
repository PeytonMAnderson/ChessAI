import time
import copy

from chess_ai.chess_logic.chess_board import ChessBoard, ChessBoardState
from chess_ai.chess_logic.chess_utils import ChessUtils
from chess_ai.chess_logic.chess_piece import ChessPiece
from chess_ai.chess_logic.chess_move import ChessMove
from chess_ai.chess_logic.chess_score import ChessScore

def draw_board(board: list):
    rank_i = 0
    print("------------------------")
    while rank_i < 8:
        rank_str = ""
        file_i = 0
        while file_i < 8:
            if board[rank_i * 8 + file_i] is None:
                rank_str += ". "
            else:
                rank_str += board[rank_i * 8 + file_i].type if board[rank_i * 8 + file_i].is_white else board[rank_i * 8 + file_i].type.lower()
                rank_str += " "
            file_i += 1
        rank_i += 1
        print(f"\t{rank_str}")
    print("------------------------")


N = 1000
UTILS = ChessUtils({"NONE": 0, "PAWN": 1, "KNIGHT": 2, "BISHOP": 3, "ROOK": 4, "QUEEN": 5, "KING": 6, "WHITE": 1, "BLACK": 2})
board = ChessBoard(UTILS).fen_to_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 0")
score = ChessScore({"PAWN": 1, "KNIGHT": 3, "BISHOP": 3, "ROOK": 4, "QUEEN": 9, "KING": 100, "CHECK": 0, "CHECKMATE": 1000})
score.calc_position_bias(board)

print("\n")

start = time.time()
for _ in range(N):
    new_board = ChessBoardState()
end = time.time()
e = round((end - start)*1000, 3)
print(f"New Empty ChessBoardState: \t\t{e} ms")

start = time.time()
for _ in range(N):
    new_board = ChessBoard(UTILS)
end = time.time()
e = round((end - start)*1000, 3)
print(f"New Empty ChessBoard: \t\t\t{e} ms")

start = time.time()
for _ in range(N):
    new_board = copy.copy(board)
end = time.time()
e = round((end - start)*1000, 3)
print(f"Copy ChessBoard: \t\t\t{e} ms")

start = time.time()
for _ in range(N):
    new_board_state = copy.copy(board.state)
end = time.time()
e = round((end - start)*1000, 3)
print(f"Copy ChessBoardState: \t\t\t{e} ms")

start = time.time()
different1 = False
different2 = False
different3 = False
for _ in range(N):
    new_board_state = ChessBoardState(board.state, board.ranks, board.files)
    old_piece: ChessPiece = board.state.piece_board[0]
    new_piece = ChessPiece(old_piece.value, old_piece.type, old_piece.is_white, old_piece.position)
    new_piece.type = "Q"
    new_board_state.piece_board[0] = new_piece
    new_board_state.whites_turn = False if new_board_state.whites_turn else True
    new_board_state.white_positions = []
    different1 = True if new_board_state.piece_board[0].type != board.state.piece_board[0].type else False
    different2 = True if new_board_state.whites_turn != board.state.whites_turn else False
    different3 = True if new_board_state.white_positions != board.state.white_positions else False
end = time.time()
e = round((end - start)*1000, 3)
print(f"New Full ChessBoardState + New Piece: \t{e} ms Board with Updated Piece: {different1} and Updated State: {different2} and different lists: {different3}")

start = time.time()
for _ in range(N):
    new_board_state = ChessBoardState(board.state)
end = time.time()
e = round((end - start)*1000, 3)
print(f"New Full ChessBoardState: \t\t{e} ms")

start = time.time()
for _ in range(N):
    new_board = ChessBoard(UTILS, board_state=board.state)
end = time.time()
e = round((end - start)*1000, 3)
print(f"New Full ChessBoard: \t\t\t{e} ms")

start = time.time()
for _ in range(N):
    new_board_state = copy.deepcopy(board.state)
end = time.time()
e = round((end - start)*1000, 3)
print(f"Deepcopy ChessBoardState: \t\t{e} ms")

start = time.time()
for _ in range(N):
    new_board = copy.deepcopy(board)
end = time.time()
e = round((end - start)*1000, 3)
print(f"Deepcopy ChessBoard: \t\t\t{e} ms")


#----------------------------------------------------------------------------------------------------------









#----------------------------------------------------------------------------------------------------------
print("\n")

start = time.time()
for _ in range(N):
    piece: ChessPiece = board.state.piece_board[0]
    board._simulate_move(ChessMove(piece, (0, 2)), board.state)
end = time.time()
e = round((end - start)*1000, 3)
print(f"Simulate Move: \t\t\t\t{e} ms")

start = time.time()
for _ in range(N):
    score.calc_score(board, board.state)
end = time.time()
e = round((end - start)*1000, 3)
print(f"Calc Score: \t\t\t\t{e} ms")

start = time.time()
for _ in range(N):
    piece: ChessPiece = board.state.piece_board[0]
    new_board = board.calc_check_status(board.state)
end = time.time()
e = round((end - start)*1000, 3)
print(f"Calc Check Status: \t\t\t{e} ms")

start = time.time()
for _ in range(N):
    piece: ChessPiece = board.state.piece_board[0]
    board.check_move_for_check(ChessMove(piece, (0, 2)), board.state)
end = time.time()
e = round((end - start)*1000, 3)
print(f"Check Move For Check: \t\t\t{e} ms")

start = time.time()
for _ in range(N):
    piece1: ChessPiece = board.state.piece_board[0]
    board.state = board._new_move(ChessMove(piece1, (2, 0)), board.state, True)
    piece2: ChessPiece = board.state.piece_board[63]
    board.state = board._new_move(ChessMove(piece2, (5, 7)), board.state, True)
    piece1: ChessPiece = board.state.piece_board[16]
    board.state = board._new_move(ChessMove(piece1, (0, 0)), board.state, True)
    piece2: ChessPiece = board.state.piece_board[47]
    board.state = board._new_move(ChessMove(piece2, (7, 7)), board.state, True)
end = time.time()
e = round((end - start)*1000, 3)
print(f"New Move (Update Self): \t\t{e} ms")

start = time.time()
for _ in range(N):
    piece: ChessPiece = board.state.piece_board[9]
    piece.calc_moves_attacks(board, board.state)
end = time.time()
e = round((end - start)*1000, 3)
print(f"Calc Moves Attacks: \t\t\t{e} ms")

start = time.time()
for _ in range(N):
    piece: ChessPiece = board.state.piece_board[0]
    new_board = board._calc_new_team_moves(board.state)
end = time.time()
e = round((end - start)*1000, 3)
print(f"Calc New Team moves: \t\t\t{e} ms")


start = time.time()
for _ in range(N):
    piece1: ChessPiece = board.state.piece_board[0]
    board.move_piece(ChessMove(piece1, (2, 0)), board.state)
    piece2: ChessPiece = board.state.piece_board[63]
    board.move_piece(ChessMove(piece2, (5, 7)), board.state)
    piece1: ChessPiece = board.state.piece_board[16]
    board.move_piece(ChessMove(piece1, (0, 0)), board.state)
    piece2: ChessPiece = board.state.piece_board[47]
    board.move_piece(ChessMove(piece2, (7, 7)), board.state)
end = time.time()
e = round((end - start)*1000, 3)
print(f"Move Piece (no copy): \t\t\t{e / 4} ms")



start = time.time()
different1 = False
for _ in range(N):
    piece: ChessPiece = board.state.piece_board[0]
    new_board = board.move_piece(ChessMove(piece, (2, 0)), board.state, True)
    different1 = True if new_board.black_positions != board.state.black_positions else False
end = time.time()
e = round((end - start)*1000, 3)
print(f"Move Piece (Copy): \t\t\t{e} ms\tDifferent Board: {different1}")
print("\n")


