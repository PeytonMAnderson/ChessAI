import tensorflow as tf
from keras.layers import Dense, Flatten, Input
import gym
import numpy as np

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

from chess_ai.chess_logic.chess_utils import ChessUtils
from chess_ai.chess_logic.chess_board import ChessBoardState, ChessBoard
from chess_ai.chess_logic.chess_piece import ChessPiece
from chess_ai.chess_logic.chess_move import ChessMove
from chess_ai.chess_logic.chess_score import ChessScore
from chess_ai.ai.neural_network.gym_env.envs.chess_env import ChessEnv
from chess_ai.ai.random.random_ai import RandomAI

MODEL_PATH = "./chess_ai/ai/neural_network/models/"
DQN_PATH =  "DQN/chess_dqn_weights.h5f"
NN_PATH =  "network/chess_neural_network.model"

PIECE_VALUES = {"NONE": 0, "PAWN": 1, "KNIGHT": 2, "BISHOP": 3, "ROOK": 4, "QUEEN": 5, "KING": 6, "WHITE": 1, "BLACK": 2}
PIECE_SCORES = {"PAWN": 1, "KNIGHT": 3, "BISHOP": 3, "ROOK": 4, "QUEEN": 9, "KING": 10, "CHECK": 0, "CHECKMATE": 1000}
NEW_BOARD = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"

#Set Up Environment
board = ChessBoard(ChessUtils(PIECE_VALUES))
board.fen_to_board(NEW_BOARD)
score = ChessScore(PIECE_SCORES, 50, 8, board)
env = ChessEnv(board, score, 50, RandomAI(False))
states = env.observation_space.shape[0]
actions = env.action_space.shape[0]


def build_agent(model, actions):
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=5000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=actions, nb_steps_warmup=5000, target_model_update=1e-2)
    return dqn


#Load Model
model = tf.keras.models.load_model(MODEL_PATH + NN_PATH)
model.summary()

#Create Agent
dqn = build_agent(model, actions)
dqn.compile(tf.keras.optimizers.legacy.Adam(learning_rate=1e-3), metrics=['mae'])

#Load Agent
dqn.load_weights(MODEL_PATH + DQN_PATH)

#Test Agent
dqn.test(env, nb_episodes=50, visualize=False)