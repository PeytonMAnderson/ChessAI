"""

    Global Variable Class for tracking colors of objects and text

"""
import yaml

from .draw_text import VisualText
from .draw_shapes import VisualShapes, Square, Node, ScoreBar

#Global Variable Class
class GlobalVisual:
    def __init__(self, 
                 
                #Settings
                w_width: int = 800,
                w_height: int = 600,
                zoom: int = 1.0,
                fontsize: int = 18,
                fontsize_title: int = 36,
                board_square_size: int = 20,
                perspective: str = "WHITE",
                world_origin: tuple = (0, 0),
                board_origin: tuple = (0, 0),

                #Colors
                colors: dict = {},
                background: tuple = (0, 0, 0),
                black_square: tuple = (0, 0, 0),
                white_square: tuple = (0, 0, 0),
                fontcolor: tuple = (0, 0, 0),
                selected: tuple = (0, 0 , 0),
                last_move_to: tuple = (0, 0, 0),
                last_move_from: tuple = (0, 0, 0),
                valid_moves: tuple = (0, 0 ,0),
                
    *args, **kwargs) -> None:
        """Graphics Handler. Controls Color, Size, Position, etc. of graphics.
        """
        
        #Settings
        self.w_width = w_width
        self.w_height = w_height
        self.zoom = zoom
        self.fontsize = fontsize
        self.fontsize_title = fontsize_title
        self.board_square_size = board_square_size
        self.world_origin = world_origin
        self.board_origin = board_origin
        self.perspective = perspective

        #Colors
        self.colors = colors
        self.fontcolor = fontcolor
        self.background_color = background
        self.board_black_color = black_square
        self.board_white_color = white_square
        self.board_selected_color = selected
        self.board_last_move_to_color = last_move_to
        self.board_last_move_from_color = last_move_from
        self.board_valid_moves_color = valid_moves

        #Visual Objects
        self.text = VisualText()
        self.shapes = VisualShapes()

    def _get_color_from_dict(self, color_name: str, color_dict: dict) -> tuple:
        """Gets the color from the color dict.

        Args:s
            color_name (str): Key string of the color
            color_dict (dict): Color dict full of keys and colors.

        Returns:
            tuple: Color.
        """
        for c_name, c_value in color_dict.items():
            if c_name == color_name:
                return c_value
        print("WARNING: Unable to determine color.")
        return (0, 0, 0)

    def _get_color(self, color: any, color_dict: dict) -> tuple:
        """Gets the color from string, list, or tuple.

        Args:
            color (any): Color string, or color in the form of a tuple or list.
            color_dict (dict): Color dict full of keys and colors.

        Returns:
            tuple: Color.
        """
        if isinstance(color, str) is True:
            return self._get_color_from_dict(color, color_dict)
        elif isinstance(color, list) is True:
            return tuple(color)
        elif isinstance(color, tuple) is True:
            return color
        else:
            print("WARNING: The color type is not supported.")
            return (0, 0, 0)
        
    def _scale_transform(self, scale_factor: float, x: float, y: float, scale_xo: float, scale_yo: float) -> tuple[float, float]:
        """Scale Transforms a point to a new location based off the scaling factor and the origin of the scale.
        Returns:
            tuple[float, float]: (x, y)
        """
        temp_x, temp_y = x - scale_xo, y - scale_yo
        new_x, new_y = temp_x * scale_factor, temp_y * scale_factor
        return new_x + scale_xo, new_y + scale_yo
    
    def _translation_transform(self, x: float, y: float, new_origin_x: int, new_origin_y: int) -> tuple[float, float]:
        """Traslates a point to a new location based off the new world origin.
        Returns:
            tuple[float, float]: (x, y)
        """
        return new_origin_x + x, new_origin_y + y
    
    def translate_world(self, new_origin_x: int, new_origin_y: int) -> None:
        #Translate board
        square: Square
        for square in self.shapes.board:
            square.x, square.y = self._translation_transform(square.x, square.y, new_origin_x, new_origin_y)
    
    def scale_world(self, scale_factor: float, scale_xo: float, scale_yo: float) -> None:
        pass

    def get_board_origin(self) -> tuple[int, int, int]:
        """Gets the board origin from the world origin offset and board origin offset, and the size of the squares.
        Returns:
            tuple[int, int, int]: x, y, size
        """
        x0, y0 = self.world_origin
        x_b, y_b = self.board_origin
        size = self.board_square_size * self.zoom
        x, y = x0 + x_b * self.zoom, y0 + y_b * self.zoom
        return x, y, size

    def set_from_yaml(self, yaml_path: str, env) -> "GlobalVisual":
        """Updates the visuals from a yaml config file.

        Args:
            yaml_path (str): Path to yaml file.

        Returns:
            GlobalVisual: Self for chaining.
        """
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            
            #Set Colors
            colors: dict = yaml_settings['VISUAL']['COLORS']
            for color_name, color_value in colors.items():
                self.colors[color_name] = tuple(color_value)

            #Set Settings
            settings: dict = yaml_settings['VISUAL']['SETTINGS']
            self.w_width = settings['WIDTH']
            self.w_height = settings['HEIGHT']
            self.zoom = settings['ZOOM']
            self.fontsize = settings['FONTSIZE']
            self.fontsize_title = settings['FONTSIZE_TITLE']
            self.board_square_size = settings['BOARD_SQUARE_SIZE']
            self.perspective = settings['PERSPECTIVE']
            self.world_origin = tuple(settings['WORLD_ORIGIN'])
            self.board_origin = tuple(settings['BOARD_ORIGIN'])
            
            #Set Colors for certain visuals
            self.background_color = self._get_color(settings['BACKGROUND_COLOR'], self.colors)
            self.board_black_color = self._get_color(settings['BOARD_BLACK_COLOR'], self.colors)
            self.board_white_color = self._get_color(settings['BOARD_WHITE_COLOR'], self.colors)
            self.board_selected_color = self._get_color(settings['BOARD_SELECTED_COLOR'], self.colors)
            self.board_last_move_to_color = self._get_color(settings['BOARD_LAST_MOVE_TO_COLOR'], self.colors)
            self.board_last_move_from_color = self._get_color(settings['BOARD_LAST_MOVE_FROM_COLOR'], self.colors)
            self.board_valid_moves_color = self._get_color(settings['BOARD_VALID_MOVES_COLOR'], self.colors)
            self.fontcolor = self._get_color(settings['FONT_COLOR'], self.colors)
            self.shapes.create_board(self.board_origin, self.board_square_size, self.board_white_color, self.board_black_color, env)
            self.shapes.create_score_bar(self.board_origin, self.board_square_size, self.board_white_color, self.board_black_color, env)

        return self
    
    def adjust_perspective(self, rank_i: int, file_i: int, env) -> tuple[int, int]:
        """Adjusts the visual perspective of the (rank_i, file_i) pair based of from whites or blacks side.

        Args:
            rank_i (int): rank index
            file_i (int): file index
            env (_type_): The Environment

        Returns:
            tuple: New (rank_i, file_i) adjusted for the perspective.
        """
        if self.perspective == "WHITE":
            return rank_i, file_i
        else:
            return env.chess.board.ranks - rank_i - 1, env.chess.board.files - file_i - 1