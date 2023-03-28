from pygame import Surface, Rect, draw, transform, font

#from ..environment import Environment

class TextObject:
    def __init__(self, text: str, x: int, y: int, fontsize: int, color: int, align: str = "topleft", *args, **kwargs) -> None:
        self.text = text
        self.x = x
        self.y = y
        self.size = fontsize
        self.color = color
        self.align = align
        
    def draw(self, surface: Surface) -> None:
        text_font = font.Font('freesansbold.ttf', int(self.size))
        text = text_font.render(self.text, False, self.color)
        rect = text.get_rect()
        setattr(rect, self.align, (self.x, self.y))
        surface.blit(text, rect)

class VisualText:
    def __init__(self, *args, **kwargs) -> None:
        """Draws Text on the screen.
        """
        self.texts = []
        self.game_stats = {}
        self.score = None

    def generate_rank_files(self, 
                            board_origin: tuple, 
                            board_square_size: int, 
                            ranks: int, 
                            files: int, 
                            white_perspective: bool,
                            fontsize: int,
                            color: tuple
                            ) -> None:
        xo, yo = board_origin[0] - board_square_size/2, board_origin[1] + board_square_size/4
        text_list = []
        #Ranks
        for i in range(ranks):
            x, y = xo, yo + board_square_size * i
            rank_str = str(ranks - i) if white_perspective else str(ranks + 1)
            text_list.append(TextObject(rank_str, x, y, fontsize, color))
        #Files
        xo, yo = board_origin[0] + board_square_size/4, board_origin[1] - board_square_size/2
        for i in range(files):
            x, y = xo + board_square_size * i, yo 
            file_str = chr(ord('a') + i) if white_perspective else chr(ord('a') + (files - i))
            text_list.append(TextObject(file_str, x, y, fontsize, color))
        self.texts += text_list

    def generate_game_stats(self, stats_origin: tuple, fontsize: int, color: tuple):
        text_list = []
        stats_dict = {}
        x, y = stats_origin

        stats = ["TURN", "LAST_MOVE", "CHECK_STATUS", "CASTLE_AVAIL", "EN_PASSANT", "HALF_MOVES", "FULL_MOVES"]

        for stat in stats:
            text_obj = TextObject("", x, y, fontsize, color)
            text_list.append(text_obj)
            stats_dict[stat] = text_obj
            y += fontsize * 2
        self.score = TextObject("", 0, 0, fontsize, color)
        text_list.append(self.score)
        self.texts += text_list
        self.game_stats = stats_dict
    
    def update_game_stats(self, env):
        self.game_stats['TURN'].text = "TURN: WHITE" if env.chess.board.state.whites_turn else "TURN: BLACK"
        self.game_stats['LAST_MOVE'].text = "LAST MOVE: " + env.chess.last_move_str
        self.game_stats['CHECK_STATUS'].text = "CHECK STATUS: " + env.chess.check_status_str
        self.game_stats['CASTLE_AVAIL'].text = "CASTLE AVAILABILITY: " + env.chess.board.state.castle_avail
        self.game_stats['EN_PASSANT'].text = "EN PASSANT AVAILABILITY: " + env.chess.board.state.en_passant
        self.game_stats['HALF_MOVES'].text = "HALF MOVES: " + str(env.chess.board.state.half_move) + "/" + str(env.chess.max_half_moves)
        self.game_stats['FULL_MOVES'].text = "FULL MOVES: " + str(env.chess.board.state.full_move)

    def draw_all_text(self, surface: Surface, env) -> "VisualText":
        """Draws all text on the screen.

        Args:
            surface (Surface): Screen to draw text to.
            env (Environment): The Environment.

        Returns:
            VisualText: Self for chaining.
        """
        # self._draw_ranks_files(surface, env)._draw_game_stats(surface, env)
        self.update_game_stats(env)
        text: TextObject
        for text in self.texts:
            text.draw(surface)
        return self
