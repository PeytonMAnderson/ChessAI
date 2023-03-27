from pygame import Surface, Rect, draw, transform, font

from ..chess_logic.chess_piece import ChessPiece
from ..chess_logic.chess_move import ChessMove
#from ..environment import Environment

class Node:
    def __init__(self, x: int, y: int, radius: int, color: tuple, child_positions: tuple, score: int, move: ChessMove, *args, **kwargs) -> None:
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
        self.score_bar = None
    
    def create_board(self, board_origin, board_square_size, board_white_color: tuple, board_black_color: tuple, env) -> None:
        self.board = self._generate_board(board_origin, board_square_size, board_white_color, board_black_color, env)
    
    def create_score_bar(self, board_origin, board_square_size, board_white_color: tuple, board_black_color: tuple, env) -> None:
        self.score_bar = ScoreBar(board_origin[0], 
                            board_origin[1] + board_square_size * (env.chess.board.ranks + 1), 
                            board_square_size * env.chess.board.files, 
                            board_square_size/2,
                            board_white_color,
                            board_black_color
        )

    def _generate_board(self, board_origin: tuple, board_square_size: int, board_white_color: tuple, board_black_color: tuple, env) -> list:
        x, yo = board_origin
        white = True
        board_list = []
        for file in range(env.chess.board.files):
            y = yo
            for rank in range(env.chess.board.ranks):
                color = board_white_color if white else board_black_color
                board_list.append(Square(x, y, board_square_size, color))
                white = False if white else True
                y = y + board_square_size
            white = False if white else True
            x = x + board_square_size
        return board_list
    
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

    def _draw_board(self, surface: Surface, env) -> "VisualShapes":
        """Draws the chess board.

        Args:
            surface (Surface): Screen to draw to.
            env (Environment): The Environment.

        Returns:
            VisualShapes: Self for chaining.
        """
        white = True
        x, yo, size = env.visual.get_board_origin()
        for file in range(env.chess.board.files):
            y = yo
            for rank in range(env.chess.board.ranks):
                if x + size >= 0 and x <= env.visual.w_width and y + size >= 0 and y <= env.visual.w_height:
                    if white:
                        rect = Rect(x, y, size, size)
                        draw.rect(surface, env.visual.board_white_color, rect)
                    else:
                        rect = Rect(x, y, size, size)
                        draw.rect(surface, env.visual.board_black_color, rect)
                white = False if white else True
                y = y + size
            white = False if white else True
            x = x + size
        return self

    def _check_bounds(self, x: int , y: int, rank_i: int, file_i: int, env) -> bool:
        """Checks if (x,y) coordinates falls within the square (rank_i, file_i).

        Args:
            x (int): x position on screen
            y (int): y position on screen
            rank_i (int): rank index
            file_i (int): file index
            env (_type_): The environment.

        Returns:
            bool: True if (x,y) is in bounds, false if otherwise.
        """
        xo, yo, size = env.visual.get_board_origin()
        xi, yr = xo + file_i * size, yo + rank_i * size
        if x >= xi and x <= xi + size and y >= yr and y <= yr + size:
            return True
        return False

    def _select_square(self, mouse_position: tuple, env) -> tuple | None:
        """Get the square that the mouse is currently selecting.

        Args:
            mouse_position (tuple): The position of the mouse.
            env (Environment): The environment.

        Returns:
            tuple | None: A square, if any, on the chess board the mouse is over.
        """
        for rank in range(env.chess.board.ranks):
            for file in range(env.chess.board.files):
                if self._check_bounds(mouse_position[0], mouse_position[1], rank, file, env) is True:
                    return env.visual.adjust_perspective(rank, file, env)
        return None

    def _draw_pieces(self, surface: Surface, env) -> "VisualShapes":
        """Draws the pieces on the chess board.

        Args:
            surface (Surface): Screen to draw to.
            env (Environment): The Environment.

        Returns:
            VisualShapes: Self for chaining.
        """
        x, y, size = env.visual.get_board_origin()

        rank_index = 0
        while rank_index < env.chess.board.ranks:
            file_index = 0
            while file_index < env.chess.board.files:

                #Get place image from chess board
                img_x = x + file_index * size
                img_y = y + rank_index * size
                if img_x + size >= 0 and img_x <= env.visual.w_width and img_y + size >= 0 and img_y <= env.visual.w_height:
                    r, f = env.visual.adjust_perspective(rank_index, file_index, env)
                    piece: ChessPiece = env.chess.board.state.piece_board[r * env.chess.board.files + f]
                    if piece is not None:
                        color_str = "w_" if piece.is_white else "b_"
                        img  = env.piece_images[color_str + piece.type.lower()]
                        #Get Size of Piece
                        size = env.visual.board_square_size * env.visual.zoom
                        #Scale and place image on canvas
                        img = transform.scale(img, (size, size))
                        surface.blit(img, (img_x, img_y))
                file_index += 1
            rank_index += 1
        return self

    def _draw_square(self, surface: Surface, rank_i: int, file_i:int, color: tuple, env) -> "VisualShapes":
        """Draws the Highlights for the move squares.

        Args:
            surface (Surface): Screen to draw to.
            env (Environment): The Environment.

        Returns:
            VisualShapes: Self for chaining.
        """
        rd, fd = env.visual.adjust_perspective(rank_i, file_i, env)
        x_o, y_o, size = env.visual.get_board_origin()
        x, y = x_o + fd * size, y_o + rd * size
        rect = Rect(x, y, size, size)
        draw.rect(surface, color, rect)
        return self
    
    def _draw_heatmap(self, surface: Surface, piece_str: str, env):
        rank_i = 0
        while rank_i < env.chess.board.ranks:
            file_i = 0
            while file_i < env.chess.board.files:
                value = env.chess.score.calc_piece_pos_bias(piece_str, (rank_i, file_i), env.chess.board, env.chess.board.state)
                color_value = value * 255
                self._draw_square(surface, rank_i, file_i, (color_value, color_value, color_value), env)
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
            rd, fd = env.io.selected_position[0], env.io.selected_position[1]
            self._draw_square(surface, rd, fd, env.visual.board_selected_color, env)
        
            #Draw Available Positions
            if env.chess.board.state.whites_turn:
                move: ChessMove
                for move in env.chess.board.state.white_moves:
                    if move.piece.position == env.io.selected_position:
                        self._draw_square(surface, move.new_position[0], move.new_position[1], env.visual.board_valid_moves_color, env)
            else:
                move: ChessMove
                for move in env.chess.board.state.black_moves:
                    if move.piece.position == env.io.selected_position:
                        self._draw_square(surface, move.new_position[0], move.new_position[1], env.visual.board_valid_moves_color, env)

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


    def _draw_score_bar(self, surface: Surface, env) -> "VisualShapes":
        """Draws Score bar for the score of the game.

        Args:
            surface (Surface): Screen to draw to.
            env (Environment): The Environment.

        Returns:
            VisualShapes: Self for chaining.
        """
        #Draw White bar
        x_o, y_o, size = env.visual.get_board_origin()
        x, y = x_o, y_o + size * env.chess.board.ranks + size/2
        bar_size = size * env.chess.board.files
        white_rect = Rect(x, y, bar_size, size/2)
        draw.rect(surface, env.visual.colors['WHITE'], white_rect)

        #Draw Black Bar
        score_diff = env.chess.score.score
        score_total = env.chess.score.score_max
        score_black = score_total - score_diff
        score_ratio: float = 0.5

        #Get score ratio, clamped to max score
        if abs(score_diff) > score_total or score_total == 0:
            if score_diff > 0:
                score_ratio = 0.0
            else:
                score_ratio = 1.0
        else:
            score_ratio = score_black / (score_total * 2)

        #Draw bar
        black_size = score_ratio * bar_size
        black_rect = Rect(x, y, black_size, size/2)
        draw.rect(surface, env.visual.colors['GRAY'], black_rect)
        env.visual.text.draw_score_text(surface, x + black_size, y, score_diff, size/2, env)
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
                




    def draw_all_shapes(self, surface: Surface, env) -> "VisualShapes":
        """Draws All shapes on the screen.

        Args:
            surface (Surface): Screen to draw to.
            env (Environment): The Environment.

        Returns:
            VisualShapes: Self for chaining.
        """
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
        
        
        # self._draw_board(surface, env)._draw_highlights(surface, env)._draw_pieces(surface, env)
        # self._draw_score_bar(surface, env)._draw_selected_piece(surface, env)
        # self.draw_tree(surface, env)
        # board_origin = env.visual.get_board_origin()
        # draw.circle(surface, env.visual.colors["RED"], (env.visual.world_origin[0], env.visual.world_origin[1]), self.width/2 * env.visual.zoom)
        # draw.circle(surface, env.visual.colors["GREEN"], (board_origin[0], board_origin[1]), self.width/2 * env.visual.zoom)
        # xb = board_origin[0] + env.visual.board_square_size * env.visual.zoom * env.chess.board.files
        # yb = board_origin[1] + env.visual.board_square_size * env.visual.zoom * env.chess.board.ranks
        # draw.circle(surface, env.visual.colors["BLUE"], (xb, yb), self.width/2 * env.visual.zoom)
        return self
    


