
import tensorflow as tf

from chess_ai.ai.policy_network.data import get_formated_data

CONFIG_FILE = "./chess_config.yaml"
TRAIN_DATA_FILE_PATH = "./chess_ai/ai/policy_network/train_data/train.json"
MODEL_FILE_PATH = './chess_ai/ai/policy_network/models'
CONV_SIZE = 32
CONV_DEPTH = 4
DENSE_NEURONS = 64
MODEL_NAME = "policy_network2.model"

def _create_network(example_boards: list, conv_size: int, conv_depth: int, dense_neurons: int = 64):
    board_count = len(example_boards)
    rank_count = len(example_boards[0])
    file_count =  len(example_boards[0][0])
    model_input = tf.keras.layers.Input(shape=(board_count, rank_count, file_count))
    conv_layer = model_input
    for _ in range(conv_depth):
        conv_layer = tf.keras.layers.Conv2D(filters=conv_size, kernel_size=3, padding='same', activation='relu')(conv_layer)
    flat_layer = tf.keras.layers.Flatten()(conv_layer)
    dense_layer = tf.keras.layers.Dense(dense_neurons, 'relu')(flat_layer)
    dense_layer = tf.keras.layers.Dense(dense_neurons, 'relu')(dense_layer)
    output_layer = tf.keras.layers.Dense(1, 'sigmoid')(dense_layer)
    return tf.keras.models.Model(inputs=model_input, outputs=output_layer)

def main():
    #Get Input Data Size
    print("Creating Model...")
    x_train, y_train = get_formated_data(TRAIN_DATA_FILE_PATH)

    #Create Model
    model = _create_network(x_train[0], CONV_SIZE, CONV_DEPTH, DENSE_NEURONS)
    model.compile(optimizer=tf.keras.optimizers.Adam(5e-4), loss='mean_squared_error')
    model.summary()

    #Train Model for 1 Epoch
    model.fit(x_train, y_train, batch_size=2048, epochs=1, verbose=1, validation_split=0.1)

    #Save Model
    print("Saving Model...")
    model.save(MODEL_FILE_PATH + "/" + MODEL_NAME)
    print("Finished!")

if __name__ == "__main__":
    main()