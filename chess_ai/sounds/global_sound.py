"""

    Global Variable Class for tracking gamestate

"""
import yaml
import pygame

#Global Variable Class
class GlobalSound:
    def __init__(self,
                volume: int = 100,
    *args, **kwargs) -> None:
        """Sound Handler. Keeps track of Sound variables.

        Args:
            volume (int, optional): Volume of all game sounds. Defaults to 100.
        """
        self.volume = volume
        
    def set_from_yaml(self, yaml_path: str) -> "GlobalSound":
        """Sets Sound variables from yaml config file.

        Args:
            yaml_path (str): Path to yaml file.

        Returns:
            GlobalSound: Self for chaining.
        """
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            settings = yaml_settings['SOUND']

            #Set settings
            self.volume = settings['VOLUME']
        return self
    
    def set_volumes(self, env) -> "GlobalSound":
        """Sets the volumes of all the sounds.

        Args:
            sound (dict): Dict of sounds

        Returns:
            GlobalSound: Self for chaining.
        """
        sound: pygame.mixer.Sound
        for sound in env.game_sounds.values():
            print(f"Setting volume to {self.volume}")
            sound.set_volume(self.volume)
    
    def play(self, sound_str: str, env) -> "GlobalSound":
        """Plays a sound.

        Args:
            sound_Str (str): The key for which sound to play
            env (Environment): The Environment.

        Returns:
            GlobalSound: Self for chaining.
        """
        env.game_sounds[sound_str].play()