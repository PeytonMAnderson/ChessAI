
import tensorflow as tf
import numpy as np

def create_network(boards: np.ndarray, conv_size: int, conv_depth: int, dense_neurons: int = 64):
    board_count = len(boards)
    rank_count = len(boards[0])
    file_count = len(boards[0][0])    
    model_input = tf.keras.layers.Input(shape=(board_count, rank_count, file_count))
    conv_layer = model_input
    for _ in range(conv_depth):
        conv_layer = tf.keras.layers.Conv2D(filters=conv_size, kernel_size=3, padding='same', activation='relu')(conv_layer)
    flat_layer = tf.keras.layers.Flatten()(conv_layer)
    dense_layer = tf.keras.layers.Dense(dense_neurons, 'relu')(flat_layer)
    output_layer = tf.keras.layers.Dense(1, 'sigmoid')(dense_layer)
    return tf.keras.models.Model(inputs=model_input, outputs=output_layer)



boards = np.zeros((14, 8, 8))
model = create_network(boards, 32, 4, 64)
model.summary()

    