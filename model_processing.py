import tf_keras as keras
import tensorflow as tf
import numpy as np

class Model:
    def __init__(self, model_path):
        # We use the legacy tf_keras loader which is better at handling older .h5 files
        self.model = keras.models.load_model(model_path, compile=False)

    def get_prediction(self, input, class_file=None):
        if class_file is None:
            # Added verbose=0 to keep the console clean
            prediction = self.model.predict(input, verbose=0)
            pred = np.argmax(prediction[0])
        else:
            prediction = [self.model.predict(char, verbose=0) for char in input]

            with open(class_file, 'r') as f:
                classes = [line.strip() for line in f]
            predictions = [classes[np.argmax(y)] for y in prediction]

            pred = "".join(predictions)

        # Use the legacy backend to clear the session
        keras.backend.clear_session()
        print(f"Result: {pred}")
        return pred