import gym
from gym import spaces
import pygame
import numpy as np
import random

from chess_ai.ai.base_ai import BaseAI
from chess_ai.chess_logic.chess_utils import ChessUtils
from chess_ai.chess_logic.chess_board import ChessBoardState, ChessBoard
from chess_ai.chess_logic.chess_piece import ChessPiece
from chess_ai.chess_logic.chess_move import ChessMove
from chess_ai.chess_logic.chess_score import ChessScore


class ChessEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, chess_board: ChessBoard, chess_score: ChessScore, max_half_moves: int, other_player: BaseAI, render_mode=None, size=5):
       
        self.chess_board = chess_board
        self.chess_score = chess_score
        self.max_half_moves = max_half_moves
        self.starting_position = chess_board.board_to_fen()
        self.other_player = other_player
        self.reward_bounds = (-chess_score.piece_scores['CHECKMATE'], chess_score.piece_scores['CHECKMATE'])
        self.board_values = [

            ("white_pawns", True, "P"),
            ("white_knights",True, "N"),
            ("white_bishops",True, "B"),
            ("white_rooks",True, "R"),
            ("white_queens",True, "Q"),
            ("white_kings",True, "K"),

            ("black_pawns", False, "P"),
            ("black_knights", False, "N"),
            ("black_bishops", False, "B"),
            ("black_rooks", False, "R"),
            ("black_queens", False, "Q"),
            ("black_kings", False, "K"),

            ("legal_moves", None, None),
        ]
        self.move_values = [
            ("old_position"),
            ("new_position"),
        ]
        self.obs_boards = len(self.board_values)
        self.act_boards = len(self.move_values)

        #Set Observation of current Chess Board
        self.observation_space = spaces.MultiBinary(self.obs_boards * self.chess_board.ranks * self.chess_board.files)
        self.observation = np.zeros(self.obs_boards * self.chess_board.ranks * self.chess_board.files, dtype=int)
        self._set_obs(chess_board.state)
        print(self.observation.shape[0])

        #Set Actions Arrays
        self.action_space = spaces.MultiBinary(self.act_boards * self.chess_board.ranks * self.chess_board.files)
        self.action = np.zeros(self.act_boards * self.chess_board.ranks * self.chess_board.files, dtype=int)
        print(self.action.shape[0])

        #Rendering
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self.window = None
        self.clock = None

    def _set_obs(self, board_state: ChessBoardState = None) -> "ChessEnv":
        #Get Piece Positions
        this_board_state = board_state if board_state is not None else self.chess_board.state
        for i in range(self.obs_boards-1):
            board_offset = i * self.chess_board.ranks * self.chess_board.files
            for r in range(self.chess_board.ranks):
                for f in range(self.chess_board.files):
                    piece: ChessPiece = this_board_state.piece_board[r * self.chess_board.files + f]
                    if piece is None or piece.is_white is not self.board_values[i][1] or piece.type != self.board_values[i][2]:
                        self.observation[board_offset + r * self.chess_board.files + f] = 0
                    else:
                        self.observation[board_offset + r * self.chess_board.files + f] = 1
        #Set to all 0
        board_offset = (self.obs_boards-1) * self.chess_board.ranks * self.chess_board.files
        for r in range(self.chess_board.ranks):
            for f in range(self.chess_board.files):
                self.observation[board_offset + r * self.chess_board.files + f] = 0
        #Get Moves
        moves_list = this_board_state.white_moves if this_board_state.whites_turn else this_board_state.black_moves
        move: ChessMove
        for move in moves_list:
            r, f = move.new_position
            self.observation[board_offset + r * self.chess_board.files + f] = 1
        return self

    def _get_obs(self) -> dict:
        boards = {}
        for i in range(self.obs_boards):
            new_board = []
            board_offset = i * self.chess_board.ranks * self.chess_board.files
            for r in range(self.chess_board.ranks):
                new_rank = []
                rank_offset = r * self.chess_board.files
                for f in range(self.chess_board.files):
                    new_rank.append(self.observation[board_offset + rank_offset + f])
                new_board.append(new_rank)
            boards[self.board_values[i][0]] = new_board
        return boards
    
    def _set_act(self, move: ChessMove) -> "ChessEnv":
        ro, fo = move.piece.position
        rf, ff = move.new_position
        self.action = np.zeros(self.act_boards * self.chess_board.ranks * self.chess_board.files, dtype=int)
        board_offset = self.chess_board.ranks * self.chess_board.files
        self.action[ro * self.chess_board.files + fo] = 1
        self.action[board_offset + rf * self.chess_board.files + ff] = 1
        return self

    def _get_act(self, action: np.ndarray) -> ChessMove | None:
        #Get starting position and ending positions from action
        ro, fo = None, None
        rf, ff = None, None
        for i in range(self.act_boards):
            board_offset = i * self.chess_board.ranks * self.chess_board.files
            for r in range(self.chess_board.ranks):
                rank_offset = r * self.chess_board.files
                for f in range(self.chess_board.files):
                    if action[board_offset + rank_offset + f] == 1:
                        if i == 0:
                            ro, fo = r, f
                        else:
                            rf, ff = r, f
        #From the starting position to ending position, find if there exists a valid move
        moves_list = self.chess_board.state.white_moves if self.chess_board.state.whites_turn else self.chess_board.state.black_moves
        move: ChessMove
        for move in moves_list:
            mro, mfo = move.piece.position
            mrf, mff = move.new_position
            if (mro, mfo) == (ro, fo) and (mrf, mff) == (rf, ff):
                return move
        return None
    
    def _calc_half_move(self, move: ChessMove) -> tuple[float, bool]:
        self.chess_board.move_piece(move, self.chess_board.state)
        score = self.chess_score.calc_score(self.chess_board, self.chess_board.state)
        terminated = False
        if (self.chess_board.state.check_status is not None 
            and abs(self.chess_board.state.check_status) == 2 
            or self.chess_board.state.check_status == 0
            or self.chess_board.state.half_move >= self.max_half_moves):
            terminated = True
        return score, terminated

    def step(self, action: np.ndarray) -> tuple[dict, float, bool, str]:
        #If move is illegal, return player resigns
        move: ChessMove = self._get_act(action)
        if move is None:
            if self.chess_board.state.whites_turn:
                return self._get_obs(), self.reward_bounds[0], True, self.chess_board.board_to_fen()
        
        #Else, Perform move our move
        wht = True if self.chess_board.state.whites_turn else False
        score, terminated = self._calc_half_move(move)
        if terminated:
            self._set_obs()
            return self._get_obs(), score if wht else -score, terminated, self.chess_board.board_to_fen()
        
        #Else Perform their move
        their_move = self.other_player.get_move(self.chess_board)
        if their_move is None:
            self._set_obs()
            return self._get_obs(), self.reward_bounds[1], True, self.chess_board.board_to_fen()
        score, terminated = self._calc_half_move(their_move)
        self._set_obs()
        return self._get_obs(), score if wht else -score, terminated, self.chess_board.board_to_fen()
    
    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        #Update the Board, observation, and action
        self.observation = np.zeros(self.obs_boards * self.chess_board.ranks * self.chess_board.files, dtype=int)
        self.chess_board.fen_to_board(self.starting_position)
        self._set_obs()
        self.action = np.zeros(self.act_boards * self.chess_board.ranks * self.chess_board.files, dtype=int)

        if self.render_mode == "human":
            self._render_frame()

        return self._get_obs(), self.starting_position

    def render(self):
        if self.render_mode == "rgb_array" or self.render_mode == "human":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        pix_square_size = (
            int(self.window_size / self.size)
        )  # The size of a single grid square in pixels

        # First we draw the target
        pygame.draw.rect(
            canvas,
            (255, 0, 0),
            pygame.Rect(
                (pix_square_size * self._target_location[0], pix_square_size * self._target_location[1]),
                (pix_square_size, pix_square_size),
            )
        )
        # Now we draw the agent
        pygame.draw.circle(
            canvas,
            (0, 0, 255),
            ((self._agent_location[0] + 0.5) * pix_square_size, (self._agent_location[1] + 0.5) * pix_square_size),
            pix_square_size / 3,
        )

        # Finally, add some gridlines
        for x in range(self.size + 1):
            pygame.draw.line(
                canvas,
                0,
                (0, pix_square_size * x),
                (self.window_size, pix_square_size * x),
                width=3,
            )
            pygame.draw.line(
                canvas,
                0,
                (pix_square_size * x, 0),
                (pix_square_size * x, self.window_size),
                width=3,
            )

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )
        
    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()