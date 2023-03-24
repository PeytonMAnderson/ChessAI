"""

    Global Variable Class for tracking Chess Variables

"""
import yaml
from copy import deepcopy

from .chess_move import ChessMove
from .chess_piece import ChessPiece
from .chess_utils import ChessUtils
from .chess_board import ChessBoard
from .chess_history import ChessHistory
from .chess_score import ChessScore


#Global Variable Class
class GlobalChess:
    def __init__(self,
                 board_files: int = 8,
                 board_ranks: int = 8,
                 max_half_moves: int = 50,
                 piece_values: dict = {},
                 piece_scores: dict = {},
    *args, **kwargs) -> None:
        
        #Attach Chess Objects
        self.board = ChessBoard(ChessUtils(piece_values), board_ranks, board_files)
        self.score = ChessScore(piece_scores)
        self.history = ChessHistory()
        self.check_status_str = "None"
        self.last_move_str = "None"
        self.last_move_tuple = None
        self.game_ended = False
        self.max_half_moves = max_half_moves
    
    def _calc_check_status_str(self) -> "GlobalChess":
        """Calculates and sets the check_status_str from check_status.

        Args:
            board (ChessBoard): The board that contains the check_status

        Returns:
            GlobalChess: Self for chaining.
        """
        if self.board.state.check_status is None:
            self.check_status_str = "None"
        elif self.board.state.check_status == 2:
            self.check_status_str = "White Checkmate"
        elif self.board.state.check_status == 1:
            self.check_status_str = "White Check"
        elif self.board.state.check_status == 0:
            self.check_status_str = "Stalemate"
        elif self.board.state.check_status == -1:
            self.check_status_str = "Black Check"
        elif self.board.state.check_status == -2:
            self.check_status_str = "Black Checkmate"
        return self
    
    def _calc_move_str(self, old_move: ChessMove, old_piece: ChessPiece | None, new_check_status: int = None) -> str:
        """Generates a Move string such as (e4, Rxf7, Qf1+, etc.)

        Args:
            move (ChessMove): The move that is about to be taken.
            board (ChessBoard): The board before the move to determine if a capture occured.

        Returns:
            str: A Move string detailing the move that will be taken.
        """
        #Get rank and file str
        rank = self.board.utils.get_rank_from_number(old_move.new_position[0], self.board.ranks)
        file = self.board.utils.get_file_from_number(old_move.new_position[1])

        #Get Castle String
        if old_move.castle:
            if old_move.new_position[1] - old_move.piece.position[1] > 0:
                return "O-O"
            else:
                return "O-O-O"

        #Get check string
        check_str = ""
        if new_check_status is not None:
            if abs(new_check_status) == 2:
                check_str = "#"
            elif abs(new_check_status) == 1: 
                check_str = "+"
        
        #Get piece str
        piece_str = ""
        if old_move.piece.type != "P":
            piece_str = old_move.piece.type
        else:
            prev_file = self.board.utils.get_file_from_number(old_move.piece.position[1])
            if prev_file != file:
                piece_str = prev_file

        #Get Piece was captured
        captured_str = ""
        if old_piece is not None:
            captured_str = "x"
        return piece_str + captured_str + file + rank + check_str

    def move_piece(self, move: ChessMove, env = None) -> "GlobalChess":
        """Moves a piece on the board assuming the move if valid. Updates score, history, game_ended, and last move.

        Args:
            move (ChessMove): The move that will be taken place.

        Returns:
            GlobalChess: Self for chaining.
        """
        if self.game_ended is True:
            return

        #Move Piece
        old_piece = deepcopy(self.board.state.piece_board[move.new_position[0] * self.board.files + move.new_position[1]])
        old_move = deepcopy(move)
        self.last_move_tuple = (move.piece.position[0], move.piece.position[1], move.new_position[0], move.new_position[1])
        self.board.move_piece(move, self.board.state)
        self._calc_check_status_str()
        self.last_move_str = self._calc_move_str(old_move, old_piece, self.board.state.check_status)

        #Get score
        self.score.update_score(self.board, self.board.state)

    
        #Calc if game ended
        if self.board.state.check_status is not None and abs(self.board.state.check_status) == 2 or self.board.state.check_status == 0:
            self.game_ended = True
        elif self.board.state.half_move >= self.max_half_moves:
            self.game_ended = True
        else:
            self.game_ended = False
        fen = self.board.board_to_fen()
        print(fen)
        self.history.pop_add({"last_move_str": self.last_move_str, 
                              "last_move_tuple": self.last_move_tuple, 
                              "fen_string":fen})
        
        if env is not None:
            if self.last_move_str.count("x") > 0:
                env.sound.play("capture", env)
            else:
                env.sound.play("move-self", env)

    def load_from_history(self, frame: dict) -> "GlobalChess":
        """Load a state of the game from history. Updates score, history, game_ended, and last move.

        Args:
            frame (dict): The frame data that will be used to update the state.
                        Includes:
                            "last_move_str"
                            "last_move_tuple"
                            "fen_string"

        Returns:
            GlobalChess: Self for chaining.
        """
        self.board.fen_to_board(frame['fen_string'])
        self.last_move_str = frame['last_move_str']
        self.last_move_tuple = frame['last_move_tuple']
        self.score.update_score(self.board, self.board.state)
        self._calc_check_status_str()

        #Calc if game ended
        if self.board.state.check_status is not None and abs(self.board.state.check_status) == 2 or self.board.state.check_status == 0:
            self.game_ended = True
        elif self.board.state.half_move >= self.max_half_moves:
            self.game_ended = True
        else:
            self.game_ended = False

    def set_from_yaml(self, yaml_path: str) -> "GlobalChess":
        """Set up chess from yaml config file.

        Args:
            yaml_path (str): Path to the config file.

        Returns:
            GlobalChess: Self for chaining.
        """
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            settings = yaml_settings['CHESS']

            #Save Board Chess Values
            self.board.files = settings['BOARD_FILES']
            self.board.ranks = settings['BOARD_RANKS']
            self.board.utils.piece_values = settings['PIECE_VALUES']
            self.score.piece_scores = settings['PIECE_SCORES']
            self.board.fen_to_board(settings['BOARD'])
            self.max_half_moves = settings['MAX_HALF_MOVES']
            self.score.set_max_score(self.board, self.board.state)

            #Start history
            self.history.pop_add({"last_move_str": "None", "last_move_tuple": None, "fen_string": settings['BOARD']})
        return self