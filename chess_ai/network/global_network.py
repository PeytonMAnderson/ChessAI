"""

    Global Variable Class for networking

"""
import yaml
import socketio

#Global Variable Class
class GlobalNetwork:
    def __init__(self,
                address: str = '192.168.1.22',
                port: str = '8800',
    *args, **kwargs) -> None:
        """Sound Handler. Keeps track of Sound variables.

        Args:
            volume (int, optional): Volume of all game sounds. Defaults to 100.
        """
        self.address = address
        self.port = port

    def set_from_yaml(self, yaml_path: str) -> "GlobalNetwork":
        """Sets Sound variables from yaml config file.

        Args:
            yaml_path (str): Path to yaml file.

        Returns:
            GlobalSound: Self for chaining.
        """
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            settings = yaml_settings['NETWORK']

            #Set settings
            self.address = settings['ADDRESS']
            self.port = settings['PORT']
        return self