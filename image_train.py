import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import json

# Path to the dataset
dataset_path = "D:/workspace/python/folder_manager/dataset/images"

# Image dimensions and batch size
IMG_HEIGHT, IMG_WIDTH = 224, 224
BATCH_SIZE = 32

# Step 1: Prepare the dataset
train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,  # Preprocessing specific to MobileNetV2
    validation_split=0.2,                    # Split dataset into training and validation (80/20)
)

# Load training and validation data
train_generator = train_datagen.flow_from_directory(
    dataset_path,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode="categorical",  # Multi-class classification
    subset="training",
)

validation_generator = train_datagen.flow_from_directory(
    dataset_path,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="validation",
)

# Step 2: Load pre-trained MobileNetV2 as the base model
base_model = MobileNetV2(
    weights="imagenet",     # Use pre-trained weights
    include_top=False,      # Exclude the final fully connected layer
    input_shape=(IMG_HEIGHT, IMG_WIDTH, 3),
)

# Freeze the base model layers
base_model.trainable = False

# Step 3: Add custom classification layers
model = Sequential([
    base_model,
    GlobalAveragePooling2D(),              # Global pooling instead of flattening
    Dropout(0.3),                          # Add dropout to reduce overfitting
    Dense(256, activation="relu"),         # Fully connected layer
    Dropout(0.3),                          # Add another dropout layer
    Dense(train_generator.num_classes, activation="softmax"),  # Output layer
])

# Step 4: Compile the model
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="categorical_crossentropy",  # Loss for multi-class classification
    metrics=["accuracy"],
)

# Step 5: Train the model
EPOCHS = 10

history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=validation_generator,
)

# Step 6: Save the trained model
model.save("models/image_classifier_model.h5")
print("Model saved as 'image_classifier_model.h5'")

# Save the class labels to a JSON file
class_labels = list(train_generator.class_indices.keys())
with open("models/class_labels.json", "w") as json_file:
    json.dump(class_labels, json_file)
print("Class labels saved as 'class_labels.json'")
