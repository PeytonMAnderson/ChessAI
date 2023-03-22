from pygame import Surface, Rect, draw, transform

from ..chess_logic.chess_piece import ChessPiece
from ..chess_logic.chess_move import ChessMove
#from ..environment import Environment

class VisualShapes:
    def __init__(self, *args, **kwargs) -> None:
        """Draws Shapes on the sreeen.
        """
        pass

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
        white = False
        x, yo, size = env.visual.get_board_origin()
        for file in range(env.chess.board.files):
            y = yo
            for rank in range(env.chess.board.ranks):
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
                r, f = env.visual.adjust_perspective(rank_index, file_index, env)
                piece: ChessPiece = env.chess.board.piece_board[r * env.chess.board.files + f]
                if piece is not None:
                    color_str = "w_" if piece.is_white else "b_"
                    img  = env.piece_images[color_str + piece.type.lower()]
                    #Get Size of Piece
                    size = env.visual.board_square_size * env.visual.zoom
                    #Get Position of Piece
                    img_x = x + file_index * size
                    img_y = y + rank_index * size
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
    
    def _draw_highlights(self, surface: Surface, env) -> "VisualShapes":
        """Draws the Highlights on the chess board for selected piece and last move.

        Args:
            surface (Surface): Screen to draw to.
            env (Environment): The Environment.

        Returns:
            VisualShapes: Self for chaining.
        """
        #Draw selected position
        if env.io.selected_position is not None:
            rd, fd = env.io.selected_position[0], env.io.selected_position[1]
            self._draw_square(surface, rd, fd, env.visual.board_selected_color, env)
        
            #Draw Available Positions
            if env.chess.board.whites_turn:
                move: ChessMove
                for move in env.chess.board.white_moves:
                    if move.piece.position == env.io.selected_position:
                        self._draw_square(surface, move.new_position[0], move.new_position[1], env.visual.board_valid_moves_color, env)
            else:
                move: ChessMove
                for move in env.chess.board.black_moves:
                    if move.piece.position == env.io.selected_position:
                        self._draw_square(surface, move.new_position[0], move.new_position[1], env.visual.board_valid_moves_color, env)
        
        #Draw Previous Move
        if env.chess.last_move_tuple is not None:
            ro, fo, rf, ff = env.chess.last_move_tuple
            self._draw_square(surface, ro, fo, env.visual.board_last_move_from_color, env)
            self._draw_square(surface, rf, ff, env.visual.board_last_move_to_color, env)

        for i in range(len(env.chess.board.piece_board)):
            piece: ChessPiece = env.chess.board.piece_board[i]
            if piece is not None:
                if piece.is_white:
                    self._draw_square(surface, piece.position[0], piece.position[1], env.visual.colors['ORANGE'], env)
                else:
                    self._draw_square(surface, piece.position[0], piece.position[1], env.visual.colors['PURPLE'], env)

        # for r, f in env.chess.board.black_positions:
        #     self._draw_square(surface, r, f, env.visual.colors['PURPLE'], env)
        for r, f in env.chess.board.king_positions:
            self._draw_square(surface, r, f, env.visual.colors['YELLOW'], env)
        # for move in env.chess.board.white_moves:
        #     self._draw_square(surface, move.new_position[0], move.new_position[1], env.visual.colors['RED'], env)
        # for move in env.chess.board.black_moves:
        #     self._draw_square(surface, move.new_position[0], move.new_position[1], env.visual.colors['BLUE'], env)

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
            piece: ChessPiece = env.chess.board.piece_board[r * env.chess.board.files + f]
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
        score_ratio: float
        if abs(score_diff) > score_total or score_total == 0:
            score_ratio = 1.0
        else:
            score_ratio = score_black / (score_total * 2)
        black_size = score_ratio * bar_size
        black_rect = Rect(x, y, black_size, size/2)
        draw.rect(surface, env.visual.colors['GRAY'], black_rect)
        env.visual.text.draw_score_text(surface, x + black_size, y, score_diff, size/2, env)
        return self


    def draw_all_shapes(self, surface: Surface, env) -> "VisualShapes":
        """Draws All shapes on the screen.

        Args:
            surface (Surface): Screen to draw to.
            env (Environment): The Environment.

        Returns:
            VisualShapes: Self for chaining.
        """
        #Draw Background
        self._draw_background(surface, env)._draw_board(surface, env)._draw_highlights(surface, env)._draw_pieces(surface, env)
        self._draw_score_bar(surface, env)._draw_selected_piece(surface, env)
        return self
    


