"""

    Global Variable Class for tracking gamestate

"""
import yaml

#Global Variable Class
class GlobalIO:
    def __init__(self,
                running: bool = True,
                zoom_speed: float = 0.05,
    *args, **kwargs) -> None:
        
        self.running = running
        self.zoom_speed = zoom_speed
        self.input_position = (0, 0)

        #Changing Variables
        self.selected_position = None

    def set_from_yaml(self, yaml_path: str) -> "GlobalIO":
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            settings = yaml_settings['IO']

            #Set settings
            self.running = settings['RUNNING']
            self.zoom_speed = settings['ZOOM_SPEED']
        return self

