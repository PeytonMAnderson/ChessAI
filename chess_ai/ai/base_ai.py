class BaseAI:
    def __init__(self, is_white: bool, *args, **kwargs):
        self.is_white = is_white
        
    def execute_turn(self, board: list, env):
        return