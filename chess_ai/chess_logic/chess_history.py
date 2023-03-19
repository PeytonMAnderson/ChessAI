


class ChessHistory:
    def __init__(self, history: list = [], history_position: int = 0, *args, **kwargs) -> None:
        self._history = history
        self._history_position = history_position

    def get_position(self) -> int:
        return self._history_position
    
    def set_position(self, position: int) -> "ChessHistory":
        self._history_position = position
        return self

    def reset_history(self) -> "ChessHistory":
        self._history = []
        self._history_position = 0
        return self
    
    def get_frame(self) -> dict:
        return self._history[self._history_position]
    
    def set_frame(self, frame_data: dict) -> "ChessHistory":
        self._history[self._history_position] = frame_data
        return self
    
    def add_frame(self, frame_data: dict) -> "ChessHistory":
        self._history.append(frame_data)
        return self

    def pop_frames(self) -> "ChessHistory":
        while len(self._history) - 1 > self._history_position:
            self._history.pop()
        return self
    
    def set_pos_get_frame(self, new_position: int) -> dict:
        if new_position < 0:
            print("WARNING: Negative position is not allowed.")
            return self._history[self._history_position]
        elif new_position >= len(self._history):
            print("WARNING: Position greater than history size is not allowed.")
            return self._history[self._history_position]
        else:
            self._history_position = new_position
            return self._history[self._history_position]
        
    def pop_add(self, frame_data: dict) -> "ChessHistory":
        self.pop_frames()
        self.add_frame(frame_data)
        self._history_position = len(self._history) - 1
        return self
    
    def get_previous(self) -> dict:
        new_position = self._history_position - 1
        if new_position < 0:
            new_position = 0
        self._history_position = new_position
        return self._history[self._history_position]
    
    def get_next(self) -> dict:
        new_position = self._history_position + 1
        if new_position >= len(self._history):
            new_position = len(self._history) - 1
        self._history_position = new_position
        return self._history[self._history_position]
    

