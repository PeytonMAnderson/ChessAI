
from .chess_board import ChessBoardState, ChessBoard
from .chess_piece import ChessPiece

class ChessScore:
    def __init__(self, piece_scores: dict, max_half_moves: int = 50, endgame_piece_count: int = 8, board: ChessBoard = None, *args, **kwargs) -> None:
        """Calculates the score value of a chess board_state.

        Args:
            piece_scores (dict): The values of pieces that will be used for score tracking.
        """
        self.piece_scores = piece_scores
        self.score_max = 0
        self.score = 0
        self.position_bias = {}
        self.max_pieces = 0
        self.max_half_moves = max_half_moves
        self.endgame_piece_count = endgame_piece_count
        if board is not None:
            print("Creating new Piece Bias...")
            self.calc_position_bias(board)

    def get_piece_worth(self, piece: ChessPiece):
        if piece is None:
            return 0
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
        elif piece.type == "K":
            return self.piece_scores['KING']
        else:
            return 0
        
    def get_position_difference(self, piece: ChessPiece, old_position: tuple, new_position: tuple, board: ChessBoard, board_state: ChessBoardState) -> float:
        position_old = old_position if piece.is_white else (board.ranks - old_position[0] - 1, old_position[1])
        position_new = new_position if piece.is_white else (board.ranks - new_position[0] - 1, new_position[1])
        return self.calc_piece_pos_bias(piece.type, position_new, board, board_state) - self.calc_piece_pos_bias(piece.type, position_old, board, board_state)

    def get_piece_score_king(self, piece: ChessPiece, board: ChessBoard, board_state: ChessBoardState) -> float:
        """Get the score of a piece type.

        Args:
            piece (ChessPiece): The piece on the chess board_state

        Returns:
            int: The value of the score of that piece.
        """
        if piece is None:
            return 0
        
        position = piece.position if piece.is_white else (board.ranks - piece.position[0] - 1, piece.position[1])
        if piece.type == "P":
            return self.piece_scores['PAWN'] + self.calc_piece_pos_bias("P", position, board, board_state) * 0.1
        elif piece.type == "N":
            return self.piece_scores['KNIGHT'] + self.calc_piece_pos_bias("N", position, board, board_state) * 0.1
        elif piece.type == 'B':
            return self.piece_scores['BISHOP'] + self.calc_piece_pos_bias("B", position, board, board_state) * 0.1
        elif piece.type == "R":
            return self.piece_scores['ROOK'] + self.calc_piece_pos_bias("R", position, board, board_state) * 0.1
        elif piece.type == 'Q':
            return self.piece_scores['QUEEN'] + self.calc_piece_pos_bias("Q", position, board, board_state) * 0.1
        elif piece.type == "K":

            #Add bias for end game, winning king wants to get closer, while losing king wants to get farther
            our_piece_count = len(board_state.white_positions) if piece.is_white else len(board_state.black_positions)
            their_piece_count = len(board_state.black_positions) if piece.is_white else len(board_state.white_positions)
            king_chase_bias = 0

            #If near the end of the game (Less than 8 pieces left on the board)
            if their_piece_count + our_piece_count < self.endgame_piece_count:

                #Favor king getting closer for winning team
                if our_piece_count > their_piece_count:
                    other_king = board_state.king_positions[1] if piece.is_white else board_state.king_positions[0]
                    dis = abs(other_king[0] - piece.position[0]) + abs(other_king[1] - piece.position[1])
                    dis_n = dis / (board.ranks + board.files)
                    king_chase_bias = (1 - dis_n) * 0.1

                #Disfavor other king getting close if on losing team
                elif our_piece_count < their_piece_count:
                    other_king = board_state.king_positions[1] if piece.is_white else board_state.king_positions[0]
                    dis = abs(other_king[0] - piece.position[0]) + abs(other_king[1] - piece.position[1])
                    dis_n = dis / (board.ranks + board.files)
                    king_chase_bias = dis_n * 0.1

            return self.piece_scores['KING'] + self.calc_piece_pos_bias("K", position, board, board_state) * 0.1 + king_chase_bias
        else:
            return 0

    
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
            white_score += self.get_piece_score_king(piece, board, board_state)
        black_score = 0
        for r, f in board_state.black_positions:
            piece: ChessPiece = board_state.piece_board[r * board.files + f]
            black_score += self.get_piece_score_king(piece, board, board_state)
        self.score_max = max(round(white_score, 3), round(white_score, 3))
        self.max_pieces = len(board_state.white_positions) + len(board_state.black_positions)
        return self


    def _get_base_score(self, board: ChessBoard, board_state: ChessBoardState) -> float:
        """Get the base score including both teams. Does not account for checking.

        Args:
            board_state (Chessboard_state): The chess board_state that will be used for score calculations

        Returns:
            int: The score value that was calculated.
        """
        white_score = 0
        for r, f in board_state.white_positions:
            piece: ChessPiece = board_state.piece_board[r * board.files + f]
            white_score += self.get_piece_score_king(piece, board, board_state)
        black_score = 0
        for r, f in board_state.black_positions:
            piece: ChessPiece = board_state.piece_board[r * board.files + f]
            black_score += self.get_piece_score_king(piece, board, board_state)
        return round(white_score - black_score, 3)

    def calc_score(self, board: ChessBoard, board_state: ChessBoardState) -> float:
        """Calculate the score value of the current chess board_state and places it in score.

        Args:
            board_state (Chessboard_state): The chess board_state that will be used for score calculations

        Returns:
            ChessScore: Returns self for chaining.
        """

        if board_state.half_move >= self.max_half_moves:
            return 0
        elif board_state.check_status is None:
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
        if board_state.half_move >= self.max_half_moves:
            self.score = 0
        elif board_state.check_status is None:
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
                score_map[rank_i * board.files + file_i] = (score / (r_m + f_m)) * 0.5 + 0.5
                file_i += 1
            rank_i += 1
        self.position_bias['N'] = score_map
        return self
    
    def _calc_pb_bishop(self, board: ChessBoard) -> "ChessScore":
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
                score = 0.0
                if file_i > 0 and file_i < board.files - 1:
                    score += 0.15
                if rank_i > 0 and rank_i < board.ranks - 1:
                    score += 0.15
                if rank_i > 1 and rank_i < board.ranks - 2 and file_i > 1 and file_i < board.files - 2:
                    score += 0.05
                if rank_i > 1 and rank_i < board.ranks - 3 and file_i > 2 and file_i < board.files - 3:
                    score += 0.10
                if rank_i == board.ranks - 3 and file_i > 0 and file_i < board.files - 1:
                    score += 0.10
                if rank_i == r_m or rank_i == r_m - 1 and file_i > 0 and file_i < board.files - 1:
                    if file_i < 3:
                        score += 0.10
                    elif file_i > board.files - 4:
                        score += 0.10
                if rank_i == board.ranks - 2 and (file_i == 1 or file_i == board.files - 2):
                    score += 0.10
                elif rank_i == board.ranks - 1 and (file_i == 0 or file_i == board.files - 1):
                    score += 0.30
                    
                score_map[rank_i * board.files + file_i] = score
                file_i += 1
            rank_i += 1
        for r, f in board.state.white_positions:
            piece: ChessPiece = board.state.piece_board[r * board.files + f]
            if piece.type == "B":
                r, f = r - 3, f
                score_map[r * board.files + f] += 0.2
                if f > f_m:
                    r, f = r, f + 1
                    score_map[r * board.files + f] -= 0.05
                else:
                    r, f = r, f - 1
                    score_map[r * board.files + f] -= 0.05

        self.position_bias['B'] = score_map
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
    
    
    def _calc_pb_king_early(self, board: ChessBoard) -> "ChessScore":
        """Calculates the Position Bias Map for a knight.

        Returns:
            ChessScore: Returns self for chaining.
        """
        score_map = [0] * board.ranks * board.files
        r_1, f_1 = board.ranks - 1, 0
        r_2, f_2 = board.ranks - 1, board.files - 1
        rank_i = 0
        while rank_i < board.ranks:
            file_i = 0
            while file_i < board.files:
                dis_r1, dis_f1 = abs(r_1 - rank_i), abs(f_1 - file_i)
                dis_r2, dis_f2 = abs(r_2 - rank_i), abs(f_2 - file_i)
                score_r = max(board.ranks - dis_r1, board.ranks - dis_r2)
                score_f = max(board.files - dis_f1, board.files - dis_f2)
                score = score_r + score_f
                score_map[rank_i * board.files + file_i] = score / (board.ranks + board.files)
                file_i += 1
            rank_i += 1
        self.position_bias['K_EARLY'] = score_map
        return self
    
    def _calc_pb_king_late(self, board: ChessBoard) -> "ChessScore":
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
        self.position_bias['K_LATE'] = score_map
        return self
    
    def calc_piece_pos_bias(self, piece_str: str, piece_position: tuple, board: ChessBoard, board_state: ChessBoardState):
        game_ratio = 0
        if self.max_pieces != 0:
            pieces = len(board_state.white_positions) + len(board_state.black_positions)
            game_ratio = pieces / self.max_pieces

        if piece_str == "K":
            b_early =  self.position_bias["K_EARLY"][piece_position[0] * board.ranks + piece_position[1]]
            b_late = self.position_bias["K_LATE"][piece_position[0] * board.ranks + piece_position[1]]
            return b_early * game_ratio + b_late * (1 - game_ratio)
        else:
            if len(board_state.white_positions) + len(board_state.black_positions) >= self.endgame_piece_count:
                if self.position_bias.get(piece_str) is None:
                    print(f"\n\nUNABLE TO FIND {piece_str} in {self.position_bias}\n\n")
                b_early = self.position_bias[piece_str][piece_position[0] * board.ranks + piece_position[1]]
                b_late = 1.0
                return b_early * game_ratio + b_late * (1 - game_ratio)
            else:
                return 1.0

    
    def calc_position_bias(self, board: ChessBoard) -> "ChessScore":
        """Calculates the Position Bias Maps for every type of piece.

        Returns:
            ChessScore: Returns self for chaining.
        """
        self._calc_pb_pawn(board)
        self._calc_pb_knight(board)
        self._calc_pb_bishop(board)
        self._calc_pb_rook(board)
        self._calc_pb_queen(board)
        self._calc_pb_king_early(board)
        self._calc_pb_king_late(board)
        
    
            


