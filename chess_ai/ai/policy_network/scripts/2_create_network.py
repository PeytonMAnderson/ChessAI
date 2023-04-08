
import tensorflow as tf

from chess_ai.ai.policy_network.network import create_network
from chess_ai.ai.policy_network.data import get_formated_data

CONFIG_FILE = "./chess_config.yaml"
TRAIN_DATA_FILE_PATH = "./chess_ai/ai/policy_network/train_data/train.json"
MODEL_FILE_PATH = './chess_ai/ai/policy_network/models/policy_network.model'
CONV_SIZE = 32
CONV_DEPTH = 4
DENSE_NEURONS = 64

def main():
    #Get Input Data Size
    print("Creating Model...")
    x_train, y_train = get_formated_data(TRAIN_DATA_FILE_PATH)

    #Create Model
    model = create_network(x_train[0], CONV_SIZE, CONV_DEPTH, DENSE_NEURONS)
    model.compile(optimizer=tf.keras.optimizers.Adam(5e-4), loss='mean_squared_error')
    model.summary()

    #Train Model for 1 Epoch
    model.fit(x_train, y_train, batch_size=2048, epochs=1, verbose=1, validation_split=0.1)

    #Save Model
    print("Saving Model...")
    model.save(MODEL_FILE_PATH)
    print("Finished!")

if __name__ == "__main__":
    main()