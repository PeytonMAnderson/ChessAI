
from .chess_board import ChessBoard
from .chess_utils import ChessUtils
from .chess_check import ChessCheck

class ChessScore:
    def __init__(self, utils: ChessUtils, board: ChessBoard, check: ChessCheck, piece_scores: dict = None, *args, **kwargs) -> None:
        self.utils = utils
        self.board = board
        self.check = check
        self.piece_scores = piece_scores
        self.score = 0
        self.score_max = 0

    def calc_piece_score(self, piece_value: int) -> int:
        piece_type = self.utils.get_str_from_piece_type(piece_value, self.board.piece_numbers, True)
        if piece_type == "P":
            return self.piece_scores['PAWN']
        elif piece_type == "N":
            return self.piece_scores['KNIGHT']
        elif piece_type == "B":
            return self.piece_scores['BISHOP']
        elif piece_type == "R":
            return self.piece_scores['ROOK']
        elif piece_type == "Q":
            return self.piece_scores['QUEEN']
        return 0

    def calc_team_score(self, board: list, is_white: bool) -> int:
        count = 0
        score = 0
        while count < len(board):
            piece_value = board[count]
            count += 1
            #Determine if location is a piece and that piece is the right color
            if piece_value == 0 or self.utils.get_is_white_from_piece_number(piece_value, self.board.piece_numbers) != is_white:
                continue
            score = score + self.calc_piece_score(piece_value)
        return score
    
    def update_max_score(self, board: list) -> None:
        white = self.calc_team_score(board, True)
        black = self.calc_team_score(board, False)
        self.score_max = white + black
    
    def calc_game_score(self, board: list, whites_turn: bool) -> int:
        #check_status = self.check.calc_check_status(board, whites_turn)
        check_status = None
        if check_status is None:
            white = self.calc_team_score(board, True)
            black = self.calc_team_score(board, False)
            return white - black
        else:
            if check_status == 2:
                return self.score_max / 2
            elif check_status == -2:
                return -self.score_max / 2
            elif check_status == 1:
                white = self.calc_team_score(board, True)
                black = self.calc_team_score(board, False)
                return white + 4 - black
            elif check_status == -1:
                white = self.calc_team_score(board, True)
                black = self.calc_team_score(board, False)
                return white - black - 4
            elif check_status == 0:
                return 0
    
    def update_score(self, board: list, whites_turn: bool) -> None:
        self.score = self.calc_game_score(board, whites_turn)
