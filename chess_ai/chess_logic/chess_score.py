
from .chess_board import ChessBoardState, ChessBoard
from .chess_piece import ChessPiece

class ChessScore:
    def __init__(self, piece_scores: dict, *args, **kwargs) -> None:
        """Calculates the score value of a chess board_state.

        Args:
            piece_scores (dict): The values of pieces that will be used for score tracking.
        """
        self.piece_scores = piece_scores
        self.score_max = 0
        self.score = 0

    def _get_piece_score(self, piece: ChessPiece) -> int:
        """Get the score of a piece type.

        Args:
            piece (ChessPiece): The piece on the chess board_state

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
    def get_piece_score_king(self, piece: ChessPiece) -> int:
        """Get the score of a piece type.

        Args:
            piece (ChessPiece): The piece on the chess board_state

        Returns:
            int: The value of the score of that piece.
        """
        if piece is None:
            return 0
        elif piece.type == "P":
            return self.piece_scores['PAWN']
        elif piece.type == "N":
            return self.piece_scores['KNIGHT']
        elif piece.type == 'B':
            return self.piece_scores['BISHOP']
        elif piece.type == "R":
            return self.piece_scores['ROOK']
        elif piece.type == 'Q':
            return self.piece_scores['QUEEN']
        elif piece.type == 'K':
            return self.piece_scores['KING']

    
    def set_max_score(self, board: ChessBoard, board_state: ChessBoardState) -> "ChessScore":
        """Get the max score possible (Not including Check or Checkmate)

        Args:
            board_state (Chessboard_state): The board_state that will be used to get the maximum value.

        Returns:
            ChessScore: Self for chaining.
        """
        white_score = 0
        for r, f in board_state.white_positions:
            piece: ChessPiece = board_state.piece_board[r * board.files + f]
            white_score += self._get_piece_score(piece)
        black_score = 0
        for r, f in board_state.black_positions:
            piece: ChessPiece = board_state.piece_board[r * board.files + f]
            black_score += self._get_piece_score(piece)
        self.score_max = max(white_score, black_score)
        return self

    def _get_base_score(self, board: ChessBoard, board_state: ChessBoardState) -> int:
        """Get the base score including both teams. Does not account for checking.

        Args:
            board_state (Chessboard_state): The chess board_state that will be used for score calculations

        Returns:
            int: The score value that was calculated.
        """
        white_score = 0
        for r, f in board_state.white_positions:
            piece: ChessPiece = board_state.piece_board[r * board.files + f]
            white_score += self._get_piece_score(piece)
        black_score = 0
        for r, f in board_state.black_positions:
            piece: ChessPiece = board_state.piece_board[r * board.files + f]
            black_score += self._get_piece_score(piece)
        return white_score - black_score

    def calc_score(self, board: ChessBoard, board_state: ChessBoardState) -> int:
        """Calculate the score value of the current chess board_state and places it in score.

        Args:
            board_state (Chessboard_state): The chess board_state that will be used for score calculations

        Returns:
            ChessScore: Returns self for chaining.
        """
        if board_state.check_status is None:
            return self._get_base_score(board, board_state)
        else:
            if board_state.check_status == 2:
                return self.piece_scores['CHECKMATE']
            elif board_state.check_status == 1:
                base = self._get_base_score(board, board_state)
                return base + self.piece_scores['CHECK']
            elif board_state.check_status == 0:
                return  0
            elif board_state.check_status == -1:
                base = self._get_base_score(board, board_state)
                return base -self.piece_scores['CHECK']
            elif board_state.check_status == -2:
                return -self.piece_scores['CHECKMATE']
        return 0
    
    def update_score(self, board: ChessBoard, board_state: ChessBoardState) -> "ChessScore":
        """Updates the score value of the current chess board_state and places it in score.

        Args:
            board_state (Chessboard_state): The chess board_state that will be used for score calculations

        Returns:
            ChessScore: Returns self for chaining.
        """
        if board_state.check_status is None:
            self.score = self._get_base_score(board, board_state)
        else:
            if board_state.check_status == 2:
                self.score = self.piece_scores['CHECKMATE']
            elif board_state.check_status == 1:
                base = self._get_base_score(board, board_state)
                self.score = base + self.piece_scores['CHECK']
            elif board_state.check_status == 0:
                self.score =  0
            elif board_state.check_status == -1:
                base = self._get_base_score(board, board_state)
                self.score =  base -self.piece_scores['CHECK']
            elif board_state.check_status == -2:
                self.score = -self.piece_scores['CHECKMATE']
        return self
    
            


