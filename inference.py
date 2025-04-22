import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

models_dir = "D:/workspace/btp/folder_manager/models"

# Load the trained model
model = tf.keras.models.load_model(os.path.join(models_dir, "image_classifier_model.h5"))

# Load the class labels
with open(os.path.join(models_dir, "class_labels.json"), "r") as json_file:
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

# Initialize the sentence transformer model for embeddings
# This will be lazily loaded only when needed
_embedding_model = None

def get_embedding_model():
    """
    Get or initialize the embedding model.
    First tries to load from local models directory, then downloads if not found.
    """
    global _embedding_model
    if _embedding_model is None:
        # Define local model path
        model_name = 'paraphrase-MiniLM-L6-v2'   # --------embedding model---------
        local_model_path = os.path.join(models_dir, model_name)
        
        # Try loading from local path first
        try:
            if os.path.exists(local_model_path):
                print(f"Loading embedding model from local path: {local_model_path}")
                _embedding_model = SentenceTransformer(local_model_path)
            else:
                # Download and save the model
                print(f"Downloading embedding model '{model_name}' (this may take a while)...")
                _embedding_model = SentenceTransformer(model_name)
                
                # Save the model for future use
                os.makedirs(local_model_path, exist_ok=True)
                _embedding_model.save(local_model_path)
                print(f"Model saved to: {local_model_path}")
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            # Fallback to direct loading
            _embedding_model = SentenceTransformer(model_name)
    
    return _embedding_model

def classify_text(text, categories=None):
    """
    Classify text based on semantic similarity to predefined categories.
    Args:
        text (str): The text content to classify
        categories (dict, optional): Dictionary of categories and their descriptions.If None, default categories will be used.
    Returns:
        str: The most similar category
    """
    if not text or len(text.strip()) == 0:
        return "unknown"
        
    # Default categories if none provided
    if categories is None:
        categories = {
            "books": "Educational materials, textbooks, novels, fiction, non-fiction literature",
            "documents": "Official papers, reports, certificates, formal documentation",
            "stories": "Narratives, creative writing, short stories, personal accounts",
            "assignments": "School or university homework, projects, academic tasks",
            "magazines": "Periodicals, articles, news publications, journals",
            "financials": "Financial statements, invoices, receipts, banking documents",
            "slips": "Short receipts, tickets, brief documentation, small notes",
            "technical": "Technical documentation, manuals, specifications, guides",
            "personal": "Personal letters, notes, diaries, messages",
            "academic": "Research papers, scholarly articles, academic publications"
        }
    
    # Clean and prepare the text
    text = text[:5000]  # Limit text length for processing efficiency
    
    # Get embeddings
    model = get_embedding_model()
    text_embedding = model.encode([text])
    
    # Get category embeddings
    category_texts = list(categories.values())
    category_names = list(categories.keys())
    category_embeddings = model.encode(category_texts)
    
    # Calculate similarities
    similarities = cosine_similarity(text_embedding, category_embeddings)[0]
    
    # Get the most similar category
    most_similar_idx = np.argmax(similarities)
    most_similar_category = category_names[most_similar_idx]
    similarity_score = similarities[most_similar_idx]
    
    print(f"Text classified as '{most_similar_category}' with similarity score: {similarity_score:.4f}")
    return most_similar_category

def extract_text_from_file(file_path):
    """Extract text content from various file types."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    try:
        # PDF files
        if ext == '.pdf':
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text
        
        # Word documents
        elif ext == '.docx':
            import docx
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
            
        # Text files
        elif ext in ['.txt', '.md', '.csv']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        
        # Add more file types as needed
        else:
            return ""
            
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""


