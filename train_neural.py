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

env = gym.make("CartPole-v0")
states = env.observation_space.shape[0]
actions = env.action_space.n

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

print(states, actions)
print(env._get_obs())

def build_model(states, actions):
    input0 = Input(shape=(1,states))
    flat0 = Flatten(input_shape=(1,states))(input0)
    dense0 = Dense(128, activation='relu')(flat0)
    dense1 = Dense(128, activation='relu')(dense0)
    output = tf.keras.layers.Dense(actions, activation='softmax')(dense1)
    model = tf.keras.Model(inputs=input0, outputs=output)
    return model

model = build_model(states, actions)
model.summary()

print(model.output_shape)

def build_agent(model, actions):
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=10000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=actions, nb_steps_warmup=2000, target_model_update=1e-2)
    return dqn

dqn = build_agent(model, actions)
dqn.compile(tf.keras.optimizers.legacy.Adam(learning_rate=1e-3), metrics=['mae'])

def starting_step_policy(observation: np.ndarray) -> int:
    board_offset = (env.obs_boards-2) * env.chess_board.ranks * env.chess_board.files
    pass

history: tf.keras.callbacks.History
history = dqn.fit(env, nb_steps=20000, visualize=False, verbose=1)

dqn.save_weights(MODEL_PATH + DQN_PATH, overwrite=True)
model.save(MODEL_PATH + NN_PATH)

print(f"\nDQN SAVED TO: {MODEL_PATH + DQN_PATH}")
print(f"\nNN SAVED TO: {MODEL_PATH + NN_PATH}")