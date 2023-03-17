"""

    Global Variable Class for tracking colors of objects and text

"""
import yaml

def get_color_from_dict(color_name: str, color_dict: dict) -> tuple:
    for c_name, c_value in color_dict.items():
        if c_name == color_name:
            return c_value
    print("WARNING: Unable to determine color.")
    return (0, 0, 0)

def get_color(color: any, color_dict: dict) -> tuple:
    if isinstance(color, str) is True:
        return get_color_from_dict(color, color_dict)
    elif isinstance(color, list) is True:
        return tuple(color)
    elif isinstance(color, tuple) is True:
        return color
    else:
        print("WARNING: The color type is not supported.")
        return (0, 0, 0)

#Global Variable Class
class GlobalVisual:
    def __init__(self, 
                w_width: int = 800,
                w_height: int = 600,
                zoom: int = 1.0,
                board_square_size: int = 20,
                world_origin: tuple = (0, 0),
                board_origin: tuple = (0, 0),
                background: tuple = (0, 0, 0),
                black_square: tuple = (0, 0, 0),
                white_square: tuple = (0, 0, 0),
                selected: tuple = (0, 0 ,0),
                last_move: tuple = (0, 0, 0),
                colors: dict = {},
    *args, **kwargs) -> None:
        
        #Set Variables
        self.w_width = w_width
        self.w_height = w_height
        self.zoom = zoom
        self.board_square_size = board_square_size
        self.world_origin = world_origin
        self.board_origin = board_origin
        self.background_color = background
        self.board_black_color = black_square
        self.board_white_color = white_square
        self.board_selected_color = selected
        self.board_last_move_color = last_move
        self.colors = colors

    
    def set_from_yaml(self, yaml_path: str) -> "GlobalVisual":
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
            self.board_square_size = settings['BOARD_SQUARE_SIZE']
            self.world_origin = tuple(settings['WORLD_ORIGIN'])
            self.board_origin = tuple(settings['BOARD_ORIGIN'])
            
            #Set Colors for certain visuals
            self.background_color = get_color(settings['BACKGROUND_COLOR'], self.colors)
            self.board_black_color = get_color(settings['BOARD_BLACK_COLOR'], self.colors)
            self.board_white_color = get_color(settings['BOARD_WHITE_COLOR'], self.colors)
            self.board_selected_color = get_color(settings['BOARD_SELECTED_COLOR'], self.colors)
            self.board_last_move_color = get_color(settings['BOARD_LAST_MOVE_COLOR'], self.colors)

        return self