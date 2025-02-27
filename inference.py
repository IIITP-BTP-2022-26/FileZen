import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np
import json

# Load the trained model
model = tf.keras.models.load_model("D:/workspace/python/folder_manager/models/image_classifier_model.h5")

# Load the class labels
with open("D:/workspace/python/folder_manager/models/class_labels.json", "r") as json_file:
    class_labels = json.load(json_file)

# Image dimensions
IMG_HEIGHT, IMG_WIDTH = 224, 224

def predict_image(image_path):
    """Predict the class of an image using the trained model."""
    # Load and preprocess the image
    img = image.load_img(image_path, target_size=(IMG_HEIGHT, IMG_WIDTH))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # Make predictions
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions, axis=1)[0]
    predicted_label = class_labels[predicted_class]

    return predicted_label

# Example usage
if __name__ == "__main__":
    image_path = r"D:\Docs\OBC-certificate.jpg"  # Replace with your image path
    predicted_label = predict_image(image_path)
    print(f"The predicted class for the image is: {predicted_label}")