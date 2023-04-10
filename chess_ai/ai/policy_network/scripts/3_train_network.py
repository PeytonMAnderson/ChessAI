import tensorflow as tf

from chess_ai.ai.policy_network.data import get_formated_data

CONFIG_FILE = "./chess_config.yaml"
TRAIN_DATA_FILE_PATH = "./chess_ai/ai/policy_network/train_data/train.json"
MODEL_FILE_PATH = './chess_ai/ai/policy_network/models'
MODEL_NAME = "policy_network3.model"

def main():
    #Get Input Data Size
    print("Training Model...")
    x_train, y_train = get_formated_data(TRAIN_DATA_FILE_PATH)

    #Load Model
    model = tf.keras.models.load_model(MODEL_FILE_PATH + "/" + MODEL_NAME)

    #Train Model for 1 Epoch
    model.fit(x_train, y_train, batch_size=500, epochs=1000, verbose=1, validation_split=0.1, callbacks=[
        tf.keras.callbacks.ReduceLROnPlateau(monitor='loss', patience=10),
        tf.keras.callbacks.EarlyStopping(monitor='loss', patience=15)
    ])

    #Save Model
    print("Saving Model...")
    model.save(MODEL_FILE_PATH + "/" + MODEL_NAME)
    print("Finished!")

if __name__ == "__main__":
    main()