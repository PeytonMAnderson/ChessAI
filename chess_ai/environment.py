
import os
import pygame

from .ai.global_ai import GlobalAI
from .chess_logic.global_chess import GlobalChess
from .io.global_io import GlobalIO
from .visuals.global_visual import GlobalVisual
from .sounds.global_sound import GlobalSound
from .network.global_network import GlobalNetwork


class Environment:
    def __init__(self, config_dir: str = None, pieces_dir: str = None, icons_dir: str = None, sounds_dir: str = None, *args, **kwargs) -> None:
        """An environment that handles visuals, I/O, chess, and AI

        Args:
            config_dir (str, optional): Directory to a config file if any. Defaults to None.
            pieces_dir (str, optional): Directory to pieces folder for piece images. Defaults to None.
        """
        #Set Variables
        if config_dir is not None:
            self.io = GlobalIO().set_from_yaml(config_dir)
            self.chess = GlobalChess().set_from_yaml(config_dir)
            self.ai = GlobalAI().set_from_yaml(config_dir)
            self.sound = GlobalSound().set_from_yaml(config_dir)
            self.visual = GlobalVisual().set_from_yaml(config_dir, self)
            self.network = GlobalNetwork().set_from_yaml(config_dir)
        else:
            self.io = GlobalIO()
            self.visual = GlobalVisual()
            self.chess = GlobalChess()
            self.ai = GlobalAI()
            self.sound = GlobalSound()
            self.network = GlobalNetwork()

        #Load Piece Images
        if pieces_dir is not None:
            self.piece_images = self._load_images(pieces_dir)
        
        #Load Icons
        if icons_dir is not None:
            self.icon_images = self._load_images(icons_dir)

        #Load Sounds
        if sounds_dir is not None:
            self.game_sounds = self._load_sounds(sounds_dir)
            self.sound.set_volumes(self)
        
        #Start at Main Menu
        self.gamestate = 0

    def _load_images(self, dir: str) -> "Environment":
        """Loads the image into the Environment.

        Args:
            dir (str): The dir of the folder that the images are located in.

        Returns:
            Environment: Self for chaining.
        """
        py_images = {}
        if os.path.exists(dir):
            for file in os.listdir(dir):
                d = dir + "/" + file
                piece = file.split('.')[0]
                py_images[piece] = pygame.image.load(d)
        else:
            print("WARNING: Image path not found.")
        return py_images
    
    def _load_sounds(self, dir: str) -> "Environment":
        """Loads the sounds into the Environment.

        Args:
            dir (str): The dir of the folder that the sounds are located in.

        Returns:
            Environment: Self for chaining.
        """
        py_sounds = {}
        if os.path.exists(dir):
            for file in os.listdir(dir):
                d = dir + "/" + file
                piece = file.split('.')[0]
                py_sounds[piece] = pygame.mixer.Sound(d)
        else:
            print("WARNING: Image path not found.")
        return py_sounds

    def execute_next_turn(self) -> "Environment":
        """Executes the next turn if possible.

        Returns:
            Environment: Self for chaining.
        """
        if self.chess.game_ended is False:
            self.ai.execute_turn(self.chess.board, self)
    
    def update(self, screen) -> "Environment":
        """Executes the next update of the game.

        Returns:
            Environment: The current Game Enviornment to update
        """
        self.visual.shapes.draw_all_shapes(screen, self)
        self.visual.text.draw_all_text(screen, self)

        if self.gamestate == 1:
            self.execute_next_turn()
    

