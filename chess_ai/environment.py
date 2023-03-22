
from .ai.global_ai import GlobalAI

from .chess_logic.global_chess import GlobalChess

from .io.global_io import GlobalIO

from .visuals.global_visual import GlobalVisual
from .visuals.images import load_images


class Environment:
    def __init__(self, config_dir: str = None, pieces_dir: str = None, *args, **kwargs) -> None:
        #Set Variables
        if config_dir is not None:
            self.io = GlobalIO().set_from_yaml(config_dir)
            self.visual = GlobalVisual().set_from_yaml(config_dir)
            self.chess = GlobalChess().set_from_yaml(config_dir)
            self.ai = GlobalAI().set_from_yaml(config_dir)
        else:
            self.io = GlobalIO()
            self.visual = GlobalVisual()
            self.chess = GlobalChess()
            self.ai = GlobalAI()

        #Load Piece Images
        if pieces_dir is not None:
            self.piece_images = load_images(pieces_dir)

    def execute_next_turn(self):
        if self.chess.game_ended is False:
            self.ai.execute_turn(self.chess.board.whites_turn, self.chess.board.piece_board, self)
