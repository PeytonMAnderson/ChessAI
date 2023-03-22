"""

    Global Variable Class for tracking gamestate

"""
import yaml

from .events import Events

#Global Variable Class
class GlobalIO:
    def __init__(self,
                running: bool = True,
                zoom_speed: float = 0.05,
    *args, **kwargs) -> None:
        """IO Handler. Keeps track of I/O status

        Args:
            running (bool, optional): If the game is running. Defaults to True.
            zoom_speed (float, optional): speed of zoom. Defaults to 0.05.
        """
        self.running = running
        self.zoom_speed = zoom_speed
        self.input_position = (0, 0)
        self.selected_position = None
        self.events = Events()
        
    def set_from_yaml(self, yaml_path: str) -> "GlobalIO":
        """Sets I/O variables from yaml config file.

        Args:
            yaml_path (str): Path to yaml file.

        Returns:
            GlobalIO: Self for chaining.
        """
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            settings = yaml_settings['IO']

            #Set settings
            self.running = settings['RUNNING']
            self.zoom_speed = settings['ZOOM_SPEED']
        return self

