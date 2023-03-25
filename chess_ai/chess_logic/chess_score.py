
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
        self.position_bias = {}

    def _get_piece_score(self, piece: ChessPiece, board: ChessBoard) -> int:
        """Get the score of a piece type.

        Args:
            piece (ChessPiece): The piece on the chess board_state

        Returns:
            int: The value of the score of that piece.
        """
        position = piece.position if piece.is_white else (board.ranks - piece.position[0] - 1, board.files - piece.position[1] - 1)
        if piece.type == "P":
            return self.piece_scores['PAWN'] + self.position_bias['P'][position[0] * board.ranks + position[1]]
        elif piece.type == "N":
            return self.piece_scores['KNIGHT'] + self.position_bias['N'][position[0] * board.ranks + piece.position[1]]
        elif piece.type == 'B':
            return self.piece_scores['BISHOP']
        elif piece.type == "R":
            return self.piece_scores['ROOK'] + self.position_bias['R'][position[0] * board.ranks + position[1]]
        elif piece.type == 'Q':
            return self.piece_scores['QUEEN'] + self.position_bias['Q'][position[0] * board.ranks + position[1]]
        else:
            return 0
        
    def get_piece_score_king(self, piece: ChessPiece, board: ChessBoard = None) -> int:
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
            white_score += self._get_piece_score(piece, board)
        black_score = 0
        for r, f in board_state.black_positions:
            piece: ChessPiece = board_state.piece_board[r * board.files + f]
            black_score += self._get_piece_score(piece, board)
        self.score_max = max(round(white_score, 3), round(white_score, 3))
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
            white_score += self._get_piece_score(piece, board)
        black_score = 0
        for r, f in board_state.black_positions:
            piece: ChessPiece = board_state.piece_board[r * board.files + f]
            black_score += self._get_piece_score(piece, board)
        return round(white_score - black_score, 3)

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
                self.score =  base - self.piece_scores['CHECK']
            elif board_state.check_status == -2:
                self.score = -self.piece_scores['CHECKMATE']
        return self
    
    def _calc_pb_pawn(self, board: ChessBoard) -> "ChessScore":
        """Calculates the Position Bias Map for a pawn.

        Returns:
            ChessScore: Returns self for chaining.
        """
        score_map = [0] * board.ranks * board.files
        r_m, f_m = board.ranks / 2 - 0.5, board.files / 2 - 0.5
        rank_i = 0
        while rank_i < board.ranks:
            file_i = 0
            while file_i < board.files:
                if rank_i == 0 or rank_i == board.ranks - 1:
                    score_map[rank_i * board.files + file_i] = 0.35
                elif rank_i == 1:
                    score_map[rank_i * board.files + file_i] = 1.0
                elif file_i == board.files / 2 or file_i == board.files / 2 - 1:
                    if rank_i < board.ranks - 3:
                        score_map[rank_i * board.files + file_i] = 0.75
                    elif rank_i == board.ranks - 3:
                        score_map[rank_i * board.files + file_i] = 0.35
                elif rank_i < board.ranks - 3:
                    score_f = f_m - abs(f_m - file_i)
                    score_map[rank_i * board.files + file_i] = 0.60 - rank_i / (board.ranks * 4) + score_f / (f_m*4)
                elif rank_i == board.ranks - 2:
                    score_map[rank_i * board.files + file_i] = 0.40
                else:
                    score_f = f_m - abs(f_m - file_i)
                    score_map[rank_i * board.files + file_i] = 0.40 - score_f / (f_m*2)
                file_i += 1
            rank_i += 1
        self.position_bias['P'] = score_map
        return self

    def _calc_pb_knight(self, board: ChessBoard) -> "ChessScore":
        """Calculates the Position Bias Map for a knight.

        Returns:
            ChessScore: Returns self for chaining.
        """
        score_map = [0] * board.ranks * board.files
        r_m, f_m = board.ranks / 2 - 0.5, board.files / 2 - 0.5
        rank_i = 0
        while rank_i < board.ranks:
            file_i = 0
            while file_i < board.files:
                dis_r, dis_f = abs(r_m - rank_i), abs(f_m - file_i)
                score_r = r_m - dis_r
                score_f = f_m - dis_f
                score = score_r + score_f
                score_map[rank_i * board.files + file_i] = score / (r_m + f_m)
                file_i += 1
            rank_i += 1
        self.position_bias['N'] = score_map
        return self
    
    def _calc_pb_queen(self, board: ChessBoard) -> "ChessScore":
        """Calculates the Position Bias Map for a queen.

        Returns:
            ChessScore: Returns self for chaining.
        """
        score_map = [0] * board.ranks * board.files
        r_m, f_m = board.ranks / 2 - 0.5, board.files / 2 - 0.5
        rank_i = 0
        while rank_i < board.ranks:
            file_i = 0
            while file_i < board.files:
                if rank_i > 0 and rank_i < board.ranks - 1:
                    if file_i > 0 and file_i < board.files - 1:
                        if file_i > 1 and file_i < board.files - 2 and rank_i > 1 and rank_i < board.ranks - 2:
                            score_map[rank_i * board.files + file_i] = 1.0
                        else:
                            score_map[rank_i * board.files + file_i] = 0.9
                    else:
                        score_r = r_m - abs(r_m - rank_i)
                        score_map[rank_i * board.files + file_i] = score_r / (r_m)

                else:
                    score_f = f_m - abs(f_m - file_i)
                    score_map[rank_i * board.files + file_i] = score_f / (f_m)

                file_i += 1
            rank_i += 1
        self.position_bias['Q'] = score_map
        return self
    
    def _calc_pb_rook(self, board: ChessBoard) -> "ChessScore":
        """Calculates the Position Bias Map for a knight.

        Returns:
            ChessScore: Returns self for chaining.
        """
        score_map = [0] * board.ranks * board.files
        r_m, f_m = board.ranks / 2 - 0.5, board.files / 2 - 0.5
        rank_i = 0
        while rank_i < board.ranks:
            file_i = 0
            while file_i < board.files:
                if rank_i > 1 and rank_i < board.ranks - 1 and file_i > 0 and file_i < board.files - 1:
                    score_map[rank_i * board.files + file_i] = 0.5
                elif rank_i < 2:
                    if rank_i == 1 and file_i > 0 and file_i < board.files - 1:
                        score_map[rank_i * board.files + file_i] = 1.0
                    else:
                        score_map[rank_i * board.files + file_i] = 0.75
                elif rank_i == board.ranks - 1:
                    score_f = f_m - abs(f_m - file_i)
                    score_map[rank_i * board.files + file_i] = score_f / (f_m * 2) + 0.25

                file_i += 1
            rank_i += 1
        self.position_bias['R'] = score_map
        return self

    
    def calc_position_bias(self, board: ChessBoard) -> "ChessScore":
        """Calculates the Position Bias Maps for every type of piece.

        Returns:
            ChessScore: Returns self for chaining.
        """
        self._calc_pb_pawn(board)
        self._calc_pb_knight(board)
        self._calc_pb_queen(board)
        self._calc_pb_rook(board)
    
            


