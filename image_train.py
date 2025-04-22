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

IMG_HEIGHT, IMG_WIDTH = 224, 224
BATCH_SIZE = 32

# Prepare the dataset
train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,  
    validation_split=0.2,                   
)

# Load training and validation data
train_generator = train_datagen.flow_from_directory(
    dataset_path,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="training",
)

validation_generator = train_datagen.flow_from_directory(
    dataset_path,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="validation",
)

# Load pre-trained MobileNetV2 as the base model
base_model = MobileNetV2(
    weights="imagenet",    
    include_top=False,      
    input_shape=(IMG_HEIGHT, IMG_WIDTH, 3),
)


# Freeze the base model layers
base_model.trainable = False

# Add custom classification layers
model = Sequential([
    base_model,
    GlobalAveragePooling2D(),        
    Dropout(0.3),                    
    Dense(256, activation="relu"),   
    Dropout(0.3),                    
    Dense(train_generator.num_classes, activation="softmax"), 
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
