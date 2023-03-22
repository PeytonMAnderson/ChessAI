
from .chess_board import ChessBoard
from .chess_piece import ChessPiece

class ChessScore:
    def __init__(self, piece_scores: dict, *args, **kwargs) -> None:
        """Calculates the score value of a chess board.

        Args:
            piece_scores (dict): The values of pieces that will be used for score tracking.
        """
        self.piece_scores = piece_scores
        self.score_max = 0
        self.score = 0

    def _get_piece_score(self, piece: ChessPiece) -> int:
        """Get the score of a piece type.

        Args:
            piece (ChessPiece): The piece on the chess board

        Returns:
            int: The value of the score of that piece.
        """
        if piece.type == "P":
            return self.piece_scores['PAWN']
        elif piece.type == "N":
            return self.piece_scores['KNIGHT']
        elif piece.type == 'B':
            return self.piece_scores['BISHOP']
        elif piece.type == "R":
            return self.piece_scores['ROOK']
        elif piece.type == 'Q':
            return self.piece_scores['QUEEN']
        else:
            return 0
    
    def set_max_score(self, board: ChessBoard) -> "ChessScore":
        """Get the max score possible (Not including Check or Checkmate)

        Args:
            board (ChessBoard): The board that will be used to get the maximum value.

        Returns:
            ChessScore: Self for chaining.
        """
        white_score = 0
        for r, f in board.white_positions:
            piece: ChessPiece = board.piece_board[r * board.files + f]
            white_score += self._get_piece_score(piece)
        black_score = 0
        for r, f in board.black_positions:
            piece: ChessPiece = board.piece_board[r * board.files + f]
            black_score += self._get_piece_score(piece)
        self.score_max = max(white_score, black_score)
        return self

    def _get_base_score(self, board: ChessBoard) -> int:
        """Get the base score including both teams. Does not account for checking.

        Args:
            board (ChessBoard): The chess board that will be used for score calculations

        Returns:
            int: The score value that was calculated.
        """
        white_score = 0
        for r, f in board.white_positions:
            piece: ChessPiece = board.piece_board[r * board.files + f]
            white_score += self._get_piece_score(piece)
        black_score = 0
        for r, f in board.black_positions:
            piece: ChessPiece = board.piece_board[r * board.files + f]
            black_score += self._get_piece_score(piece)
        return white_score - black_score

    def calc_score(self, board: ChessBoard) -> "ChessScore":
        """Calculate the score value of the current chess board and places it in score.

        Args:
            board (ChessBoard): The chess board that will be used for score calculations

        Returns:
            ChessScore: Returns self for chaining.
        """
        if board.check_status is None:
            self.score = self._get_base_score(board)
        else:
            if board.check_status == 2:
                self.score = self.piece_scores['CHECKMATE']
            elif board.check_status == 1:
                base = self._get_base_score(board)
                self.score = base + self.piece_scores['CHECK']
            elif board.check_status == 0:
                self.score =  0
            elif board.check_status == -1:
                base = self._get_base_score(board)
                self.score =  base -self.piece_scores['CHECK']
            elif board.check_status == -2:
                self.score = -self.piece_scores['CHECKMATE']
        return self
            


