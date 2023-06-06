from pygame import Surface, Rect, draw, transform, font

from ..chess_logic.chess_piece import ChessPiece
from ..chess_logic.chess_move import ChessMove
#from ..environment import Environment

class Node:
    def __init__(self, x: int, y: int, radius: int, color: tuple, score: int, move: ChessMove, *args, **kwargs) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.xt = self.x - self.radius * 0.25
        self.yt = self.y - self.radius * 0.25
        self.color = color
        self.score = score
        self.move = move
        self.child_positions = []

    def draw(self, surface: Surface, font: font.Font) -> None:
        for child_pos in self.child_positions:
            x2, y2 = child_pos
            draw.line(surface, self.color, (self.x, self.y), (x2, y2))
        if self.x >= 0:
            draw.circle(surface, self.color, (self.x, self.y), self.radius)
            if self.move is not None:
                text2 = f"{self.move.piece.position}->{self.move.new_position}"
                turn_text2 = font.render(text2, False, (100, 100, 255))
                surface.blit(turn_text2, (self.xt, self.yt + font.get_height()))            
            text1 = f"{self.score}"        
            turn_text = font.render(text1, False, (100, 100, 255))
            surface.blit(turn_text, (self.xt, self.yt))

class Square:
    def __init__(self, xo: int, yo: int, size: int, color: tuple, *args, **kwargs) -> None:
        self.x = xo
        self.y = yo
        self.size = size
        self.color = color

    def draw(self, surface: Surface) -> None:
        rect = Rect(self.x, self.y, self.size, self.size)
        draw.rect(surface, self.color, rect)

    def check_bounds(self, x: int, y: int):
        if x >= self.x and x <= self.x + self.size:
            if y >= self.y and y <= self.y + self.size:
                return True
        return False

class ScoreBar:
    def __init__(self, xo: int, yo: int, width: int, height: int, white_color: tuple, black_color: tuple, *args, **kwargs) -> None:
        self.x = xo
        self.y = yo
        self.width = width
        self.height = height
        self.white_color = white_color
        self.black_color = black_color
        self.ratio = 0.5
    
    def calc_ratio(self, env) -> None:
        score_diff = env.chess.score.score
        score_total = env.chess.score.score_max
        score_black = score_total - score_diff
        score_ratio: float = 0.5

        #Get score ratio, clamped to max score
        if abs(score_diff) > score_total or score_total == 0:
            score_ratio = 0.0 if score_diff > 0 else 1.0
        else:
            score_ratio = score_black / (score_total * 2)
        self.ratio = score_ratio
    
    def draw(self, surface: Surface) -> None:
        #Draw bars
        white_rect = Rect(self.x, self.y, self.width, self.height)
        draw.rect(surface, self.white_color, white_rect)
        black_size = self.ratio * self.width
        black_rect = Rect(self.x, self.y, black_size, self.height)
        draw.rect(surface, self.black_color, black_rect)

class VisualShapes:
    def __init__(self, *args, **kwargs) -> None:
        """Draws Shapes on the sreeen.
        """
        self.height = 100
        self.width = 80
        self.tree = []
        self.board = []
        self.main_menu = []
        self.score_bar = None
        self.icons = None

    def get_square(self, x: int, y: int, env) -> tuple | None:
        for ro in range(env.chess.board.ranks):
            for fo in range(env.chess.board.files):
                r, f = env.visual.adjust_perspective(env, ro, fo)
                square: Square = self.board[r * env.chess.board.ranks + f]
                if square.check_bounds(x, y):
                    return (ro, fo)
        return None
    
    def create_board(self, board_origin, board_square_size, board_white_color: tuple, board_black_color: tuple, env) -> None:
        xo, y = board_origin
        white = True
        board_list = []
        for rank in range(env.chess.board.ranks):
            x = xo
            for file in range(env.chess.board.files):
                color = board_white_color if white else board_black_color
                board_list.append(Square(x, y, board_square_size, color))
                white = False if white else True
                x += board_square_size
            white = False if white else True
            y += board_square_size
        self.board = board_list
    
    def create_score_bar(self, board_origin, board_square_size, board_white_color: tuple, board_black_color: tuple, env) -> None:
        self.score_bar = ScoreBar(board_origin[0], 
                            board_origin[1] + board_square_size * (env.chess.board.ranks + 1), 
                            board_square_size * env.chess.board.files, 
                            board_square_size/2,
                            board_white_color,
                            board_black_color
        )
    
    def update_score_bar(self, env) -> None:
        score = env.chess.score.score
        self.score_bar.calc_ratio(env)
        env.visual.text.score.y = self.score_bar.y + self.score_bar.height/4
        env.visual.text.score.text = str(score) if score <= 0 else "+" + str(score)
        if score >= 0:
            env.visual.text.score.x = self.score_bar.x + self.score_bar.width * self.score_bar.ratio + env.visual.text.score.size
            env.visual.text.score.align = "topleft"
            env.visual.text.score.color = env.visual.colors["GRAY"]
        else:
            env.visual.text.score.x = self.score_bar.x + self.score_bar.width * self.score_bar.ratio - env.visual.text.score.size
            env.visual.text.score.align = "topright"
            env.visual.text.score.color = env.visual.colors["WHITE"]

    def _tree_recurse(self, sub_tree_node: list, env, origin_x: int = 0, origin_y: int = 0):
        node_list = []
        this_node_value = sub_tree_node[0]
        this_node_sub_tree = sub_tree_node[1]
        this_node = Node(0, 0, self.width , (0,0,0), [], this_node_value[0], this_node_value[1])
        node_list.append(this_node)
        
        #Loop over children
        child_x_diff =  self.width 
        child_x, child_y = origin_x, origin_y + self.height 
        count = 0
        sqrt = int(len(this_node_sub_tree)**0.5)
        biggest_x = child_x
        smallest_x = 1000000
        biggest_y = child_y
        for node in this_node_sub_tree:
            #Depth > 0: [(best_score, best_move_list[0]), current_tree]
            if isinstance(node, list):
                sub_node_list, new_child_x, new_child_y = self._tree_recurse(node, env, child_x + child_x_diff , child_y+self.height )
                this_node.child_positions.append((sub_node_list[0].x, sub_node_list[0].y))
                node_list += sub_node_list
                smallest_x = new_child_x if new_child_x < smallest_x else smallest_x
                biggest_x = new_child_x if new_child_x > biggest_x else biggest_x
                biggest_y = new_child_y if new_child_y > biggest_y else biggest_y
                if count == sqrt:
                    child_x = origin_x
                    child_y = biggest_y
                    count = 0
                else:
                    child_x = new_child_x + child_x_diff 
                    count += 1
            #Depth == 0 (score, move)
            else:
                new_node = Node(child_x, child_y, self.width, env.visual.colors["BOARD_DARK"], [], node[0], node[1])
                this_node.child_positions.append((child_x, child_y))
                node_list.append(new_node)
                smallest_x = origin_x if origin_x < smallest_x else smallest_x
                biggest_y = child_y if child_y > biggest_y else biggest_y
                if count == sqrt:
                    biggest_x = child_x
                    child_x = origin_x
                    child_y += self.width
                    count = 0
                else:
                    child_x += child_x_diff 
                    count += 1
        this_node.x, this_node.y = smallest_x + (biggest_x-smallest_x)/2, origin_y
        this_node.color = env.visual.colors["WHITE"] if this_node_value[2] else env.visual.colors["GRAY"]
        return node_list, biggest_x, biggest_y
    
    def generate_tree(self, env):
        tree = env.chess.tree
        board_origin = env.visual.board_origin
        board_score_height = env.visual.board_square_size * (env.chess.board.ranks + 2)
        x, y = env.visual.board_origin[0], env.visual.board_origin[1] + board_score_height
        if len(tree) > 0:
            node_list, _, _ = self._tree_recurse(tree, env, x, y)
            self.tree = node_list

    def _draw_background(self, surface: Surface, env) -> "VisualShapes":
        """Draws the background.

        Args:
            surface (Surface): Screen to draw to.
            env (Environment): The Environment.

        Returns:
            VisualShapes: Self for chaining.
        """
        surface.fill(env.visual.background_color)
        return self

    def draw_pieces(self, surface: Surface, env) -> "VisualShapes":
        for rank_i in range(env.chess.board.ranks):
            for file_i in range(env.chess.board.files):
                    piece: ChessPiece = env.chess.board.state.piece_board[rank_i * env.chess.board.files + file_i]
                    if piece is not None:
                        pers_r, pers_f = env.visual.adjust_perspective(env, rank_i, file_i)
                        square: Square = self.board[pers_r * env.chess.board.files + pers_f]
                        color_str = "w_" if piece.is_white else "b_"
                        img  = env.piece_images[color_str + piece.type.lower()]
                        img = transform.scale(img, (square.size, square.size))
                        surface.blit(img, (square.x, square.y))
        return self
    
    def draw_pfp(self, surface: Surface, env) -> "VisualShapes":
        pers_r, pers_f = env.visual.adjust_perspective(env, env.chess.board.ranks-1, 0)[0], 0
        square: Square = self.board[pers_r * env.chess.board.files + pers_f]
        img_str = env.ai.white_player_str.lower()
        img = env.icon_images[img_str]
        img = transform.scale(img, (square.size, square.size))
        surface.blit(img, (square.x - square.size*2, square.y))

        pers_r, pers_f = env.visual.adjust_perspective(env, 0, 0)[0], 0
        square: Square = self.board[pers_r * env.chess.board.files + pers_f]
        img_str = env.ai.black_player_str.lower()
        img = env.icon_images[img_str]
        img = transform.scale(img, (square.size, square.size))
        surface.blit(img, (square.x - square.size*2, square.y))
        return self

    def _draw_square(self, surface: Surface, rank_i: int, file_i:int, color: tuple, env) -> "VisualShapes":
        """Draws the Highlights for the move squares.

        Args:
            surface (Surface): Screen to draw to.
            env (Environment): The Environment.

        Returns:
            VisualShapes: Self for chaining.
        """
        pers_r, pers_f = (rank_i, file_i) if env.visual.perspective == "WHITE" else (env.chess.board.ranks - rank_i - 1, env.chess.board.files - file_i - 1)
        square: Square = self.board[pers_r * env.chess.board.files + pers_f]
        rect = Rect(square.x, square.y, square.size, square.size)
        draw.rect(surface, color, rect)
        return self
    
    def _draw_heatmap(self, surface: Surface, piece_str: str, env):
        rank_i = 0
        while rank_i < env.chess.board.ranks:
            file_i = 0
            while file_i < env.chess.board.files:
                value = env.chess.score.calc_piece_pos_bias(piece_str, (rank_i, file_i), env.chess.board, env.chess.board.state)
                cv = value * 255
                self._draw_square(surface, rank_i, file_i, (cv, cv, cv), env)
                file_i += 1
            rank_i += 1
        return self
    
    def _draw_highlights(self, surface: Surface, env) -> "VisualShapes":
        """Draws the Highlights on the chess board for selected piece and last move.

        Args:
            surface (Surface): Screen to draw to.
            env (Environment): The Environment.

        Returns:
            VisualShapes: Self for chaining.
        """
        #Draw Previous Move
        if env.chess.last_move_tuple is not None:
            ro, fo, rf, ff = env.chess.last_move_tuple
            self._draw_square(surface, ro, fo, env.visual.board_last_move_from_color, env)
            self._draw_square(surface, rf, ff, env.visual.board_last_move_to_color, env)

        #Draw selected position
        if env.io.selected_position is not None:
            rd, fd = env.io.selected_position
            self._draw_square(surface, rd, fd, env.visual.board_selected_color, env)
        
            #Draw Available Positions
            if env.chess.board.state.whites_turn:
                move: ChessMove
                for move in env.chess.board.state.white_moves:
                    if move.piece.position == env.io.selected_position:
                        mr, mf = move.new_position
                        self._draw_square(surface, mr, mf, env.visual.board_valid_moves_color, env)
            else:
                move: ChessMove
                for move in env.chess.board.state.black_moves:
                    if move.piece.position == env.io.selected_position:
                        mr, mf = move.new_position
                        self._draw_square(surface, mr, mf, env.visual.board_valid_moves_color, env)

        # for position in env.chess.board.state.white_positions:
        #     self._draw_square(surface, position[0], position[1], env.visual.colors['ORANGE'], env)
        # for position in env.chess.board.state.black_positions:
        #     self._draw_square(surface, position[0], position[1], env.visual.colors['PURPLE'], env)
        # for move in env.chess.board.state.white_moves:
        #     self._draw_square(surface, move.new_position[0], move.new_position[1], env.visual.colors['RED'], env)
        # for move in env.chess.board.state.black_moves:
        #     self._draw_square(surface, move.new_position[0], move.new_position[1], env.visual.colors['BLUE'], env)
        #self._draw_heatmap(surface, "K", env)
        return self
        
    def _draw_selected_piece(self, surface: Surface, env) -> "VisualShapes":
        """Draws the Piece that has been selected under the mouse.

        Args:
            surface (Surface): Screen to draw to.
            env (Environment): The Environment.

        Returns:
            VisualShapes: Self for chaining.
        """
        if env.io.selected_position is not None:
            r, f = env.io.selected_position
            piece: ChessPiece = env.chess.board.state.piece_board[r * env.chess.board.files + f]
            if piece is not None and piece != 0:
                color_str = "w_" if piece.is_white else "b_"
                img  = env.piece_images[color_str + piece.type.lower()]
                #Get Size of Piece
                size = env.visual.board_square_size * env.visual.zoom
                #Get Position of Piece
                img_x, img_y = env.io.input_position
                img_x, img_y = img_x - size /2, img_y - size /2
                #Scale and place image on canvas
                img = transform.scale(img, (size, size))
                surface.blit(img, (img_x, img_y))
        return self


    def draw_tree(self, surface: Surface, env):
        node: Node
        xo, yo, size = env.visual.get_board_origin()
        yo = yo + size * (env.chess.board.ranks + 2)
        fontsize = int(env.visual.fontsize * env.visual.zoom * 0.5)
        rf_font = font.Font('freesansbold.ttf', fontsize)
        for node in self.tree:
            color = env.visual.colors["BOARD_DARK"] if len(node.child_positions) == 0 else env.visual.colors["WHITE"] if node.maximize else env.visual.colors["GRAY"]
            xn, yn = node.screen_position[0], node.screen_position[1]
            x, y = xo + xn * env.visual.zoom, yo + yn * env.visual.zoom
            xt, yt = x - self.width * env.visual.zoom * 0.25, y - self.width * env.visual.zoom * 0.25
            for child_pos in node.child_positions:
                x1, y1 = xo + node.screen_position[0] * env.visual.zoom, yo + node.screen_position[1] * env.visual.zoom
                x2, y2 = xo + child_pos[0] * env.visual.zoom, yo + child_pos[1] * env.visual.zoom
                draw.line(surface, color, (x1, y1), (x2, y2))
            if x >= 0 and x <= env.visual.w_width:
                draw.circle(surface, color, (x,y), self.width/2 * env.visual.zoom)
                if node.move is not None:
                    text2 = f"{node.move.piece.position}->{node.move.new_position}"
                    turn_text2 = rf_font.render(text2, False, env.visual.colors["BLUE"])
                    surface.blit(turn_text2, (xt, yt+fontsize))            
                text1 = f"{node.score}"        
                turn_text = rf_font.render(text1, False, env.visual.colors["BLUE"])
                surface.blit(turn_text, (xt, yt))

    def draw_main_menu(self, surface: Surface, env) -> "VisualShapes":
        if len(self.main_menu) == 0:
            rect = surface.get_rect()
            self.main_menu.append(Rect(rect.w/2 - 250, rect.h/2, 500, 50))
            self.main_menu.append(Rect(rect.w/2 - 250, rect.h/2 + 100, 500, 50))
        
        s_color = (100, 225, 100) if self.main_menu[0].collidepoint(env.io.input_position[0], env.io.input_position[1]) else (50, 200, 50)
        m_color = (100, 225, 100) if self.main_menu[1].collidepoint(env.io.input_position[0], env.io.input_position[1]) else (50, 200, 50)
        
        draw.rect(surface, s_color, self.main_menu[0])
        draw.rect(surface, m_color, self.main_menu[1])

    def draw_all_shapes(self, surface: Surface, env) -> "VisualShapes":
        """Draws All shapes on the screen.

        Args:
            surface (Surface): Screen to draw to.
            env (Environment): The Environment.

        Returns:
            VisualShapes: Self for chaining.
        """
        if env.gamestate == 0:
            self.draw_main_menu(surface, env)
            return

        #Draw Background
        self._draw_background(surface, env)

        #Draw Board
        square: Square
        for square in self.board:
            square.draw(surface)
        
        #Draw Bar
        if self.score_bar is not None:
            self.score_bar.draw(surface)

        #Draw Tree
        node: Node
        rf_font = font.Font('freesansbold.ttf', int(env.visual.fontsize * env.visual.zoom * 0.5))
        for node in self.tree:
            node.draw(surface, rf_font)
        
        #Draw Highlights and pieces
        self._draw_highlights(surface, env).draw_pieces(surface, env).draw_pfp(surface, env)._draw_selected_piece(surface, env)
        return self
    


