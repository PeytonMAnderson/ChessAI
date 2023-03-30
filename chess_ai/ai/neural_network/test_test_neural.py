import tensorflow as tf
from keras.layers import Dense, Flatten
import gym
import numpy as np

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

MODEL_PATH = "./chess_ai/ai/neural_network/models/"
DQN_PATH =  "DQN/dqn_weights.h5f"
NN_PATH =  "network/neural_network.model"

def build_model(states, actions):
    model = tf.keras.models.Sequential()
    model.add(Flatten(input_shape=(1,states)))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    return model

def build_agent(model, actions):
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=5000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=actions, nb_steps_warmup=10, target_model_update=1e-2)
    return dqn
env2 = gym.Env()
env = gym.make("CartPole-v0")
states = env.observation_space.shape[0]
actions = env.action_space.n
model = build_model(states, actions)
dqn = build_agent(model, actions)
dqn.compile(tf.keras.optimizers.legacy.Adam(learning_rate=1e-3), metrics=['mae'])
dqn.load_weights(MODEL_PATH + DQN_PATH)
dqn.test(env, nb_episodes=50, visualize=True)