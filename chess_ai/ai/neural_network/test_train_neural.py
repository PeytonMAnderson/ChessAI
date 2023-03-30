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

env = gym.make("CartPole-v0")
states = env.observation_space.shape[0]
actions = env.action_space.n

#episodes = 10
#for episode in range(1, episodes+1):
#    state = env.reset();
#    done = False
#    score = 0

#    while not done:
#        env.render()
#        action = random.choice([0,1])
#        n_state, reward, done, info = env.step(action)
#        score+=reward
#    print('Episode:{} Score:{}'.format(episode, score))

def build_model(states, actions):
    model = tf.keras.models.Sequential()
    model.add(Flatten(input_shape=(1,states)))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    return model

model = build_model(states, actions)

model.summary()

def build_agent(model, actions):
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=5000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=actions, nb_steps_warmup=10, target_model_update=1e-2)
    return dqn

dqn = build_agent(model, actions)
dqn.compile(tf.keras.optimizers.legacy.Adam(learning_rate=1e-3), metrics=['mae'])
dqn.fit(env, nb_steps=5000, visualize=False, verbose=1)

scores = dqn.test(env, nb_episodes=100, visualize=False)
print(np.mean(scores.history['episode_reward']))

dqn.save_weights(MODEL_PATH + DQN_PATH, overwrite=True)
#model.save(MODEL_PATH + NN_PATH)