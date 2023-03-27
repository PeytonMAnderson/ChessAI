from pygame import Surface, Rect, draw, transform, font

#from ..environment import Environment

class TextObject:
    def __init__(self, text: str, x: int, y: int, fontsize: int, color: int, *args, **kwargs) -> None:
        self.text = text
        self.x = x
        self.y = y
        self.size = fontsize
        self.color = color

    def draw(self, surface: Surface) -> None:
        text_font = font.Font('freesansbold.ttf', int(self.size))
        text = text_font.render(self.text, False, self.color)
        surface.blit(text, (self.x, self.y))

class VisualText:
    def __init__(self, *args, **kwargs) -> None:
        """Draws Text on the screen.
        """
        self.texts = []
        self.game_stats = {}

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


    def _draw_ranks_files(self, surface: Surface, env) -> "VisualText":
        """Draws the ranks and files labels on the screen.

        Args:
            surface (Surface): The screen to draw on.
            env (Environment): The environment.

        Returns:
            VisualText: Self for chaining.
        """
        x, y, size = env.visual.get_board_origin()
        fontsize = int(env.visual.fontsize_title * env.visual.zoom)
        rf_font = font.Font('freesansbold.ttf', fontsize)

        #Get Rank Origin
        xr, yr =  x - size/2, y + size/4
        for rank in range(env.chess.board.ranks):
            rank_str = env.chess.board.utils.get_rank_from_number(rank, env.chess.board.ranks, env.visual.perspective)
            rank_text = rf_font.render(rank_str, True, env.visual.fontcolor, env.visual.background_color)
            rank_pos = (xr, yr + size * rank)
            surface.blit(rank_text, rank_pos)

        #Get File Origin
        xf, yf =  x + size/3, y - size/2
        for file in range(env.chess.board.files):
            file_str = env.chess.board.utils.get_file_from_number(file, env.chess.board.files, env.visual.perspective)
            file_text = rf_font.render(file_str, True, env.visual.fontcolor, env.visual.background_color)
            file_pos = (xf + size * file, yf)
            surface.blit(file_text, file_pos)
        return self

    def _draw_game_stats(self, surface: Surface, env) -> "VisualText":
        """Draws Text for Game Stats such as Moves, Check, Turn, etc.

        Args:
            surface (Surface): The screen to draw text on.
            env (Environment): The environment.

        Returns:
            VisualText: Self for chaining.
        """
        #Get Board Origin
        xo, yo, size = env.visual.get_board_origin()
        fontsize = int(env.visual.fontsize_title * env.visual.zoom)
        x, y = xo + size * (env.chess.board.files + 1), yo
        rf_font = font.Font('freesansbold.ttf', fontsize)

        #Turn
        turn_text = rf_font.render(f"Turn: {'White' if env.chess.board.state.whites_turn else 'Black'}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
        turn_pos = (x, y)

        #Last Move:
        lm_text = rf_font.render(f"Last Move: {env.chess.last_move_str}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
        lm_pos = (x, y + fontsize * 2)

        #Check Status
        check_text = rf_font.render(f"Check: {env.chess.check_status_str}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
        check_pos = (x, y + fontsize * 4)

        #Castle Status
        castle_text = rf_font.render(f"Castle Availability: {env.chess.board.state.castle_avail}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
        castle_pos = (x, y + fontsize * 6)

        #En Passant Status
        enpass_text = rf_font.render(f"En Passant Availability: {env.chess.board.state.en_passant}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
        enpass_pos = (x, y + fontsize * 8)

        #Half Move Status
        half_text = rf_font.render(f"Half Clock: {env.chess.board.state.half_move} / {env.chess.max_half_moves}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
        half_pos = (x, y + fontsize * 10)

        #Half Move Status
        full_text = rf_font.render(f"Full Moves: {env.chess.board.state.full_move}", True, env.visual.colors['WHITE'], env.visual.colors['BLACK'])
        full_pos = (x, y + fontsize * 12)

        #Blit
        surface.blit(turn_text, turn_pos)
        surface.blit(lm_text, lm_pos)
        surface.blit(check_text, check_pos)
        surface.blit(castle_text, castle_pos)
        surface.blit(enpass_text, enpass_pos)
        surface.blit(half_text, half_pos)
        surface.blit(full_text, full_pos)
        return self  

    def draw_score_text(self, surface: Surface, xo: int, yo: int, score: int, size: int, env) -> "VisualText":
        """Draws the score text at the (xo,yo) location.

        Args:
            surface (Surface): The screen to draw text to.
            xo (int): x origin
            yo (int): y origin
            score (int): score value
            size (int): size of squares
            env (Environment): The environment

        Returns:
            VisualText: Self for chaining.
        """
        fontsize = int(env.visual.fontsize_title * env.visual.zoom / 2) 
        rf_font = font.Font('freesansbold.ttf', fontsize)
        score_str = str(score) if score < 0 else "+" + str(score)
        x_diff = size if score >= 0 else -size - fontsize
        font_color = env.visual.colors['WHITE'] if score < 0 else env.visual.colors['GRAY']
        score_text = rf_font.render(f"{score_str}", True, font_color)
        score_pos = (xo + x_diff, yo + size/4)
        surface.blit(score_text, score_pos)
        return self

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
