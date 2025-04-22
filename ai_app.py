import os
import shutil
from typing import List, Dict
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, pipeline
from PIL import Image
from PyPDF2 import PdfReader
import PyPDF2

# Initialize classification pipelines
image_classifier = pipeline("image-classification", model="google/vit-base-patch16-224")
pdf_classifier = pipeline("text-classification", model="distilbert-base-uncased")
text_classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

# Supported file extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
PDF_EXTENSIONS = {".pdf"}

CATEGORIES = {
    "Images": ["documents", "slips", "family", "college", "nature"],
    "PDFs": ["books", "documents", "stories", "assignments", "magazines", "financials", "slips"]
}

# Directory paths
SOURCE_DIR = "D:/workspace/python/folder_manager/Random"
TARGET_DIR = "D:/workspace/python/folder_manager/Organized"
MOVE_FILES = False  # Set to True to move files, False to copy files

# Ensure target directories exist
def ensure_directories(categories: List[str]):
    for category in categories:
        os.makedirs(os.path.join(TARGET_DIR, category), exist_ok=True)

# Classify an image file
def classify_image(file_path: str) -> str:
    try:
        image = Image.open(file_path).convert("RGB")
        results = image_classifier(image, top_k=1)
        print(f"\nClassification results for {file_path} ::: {results}\n")
        return results[0]["label"]
    except Exception as e:
        print(f"Error classifying image {file_path}: {e}")
        return "Unknown"

def classify_pdf(file_path: str) -> str:
    """Classify PDFs based on extracted text."""
    with open(file_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        prediction = text_classifier(text[:512])  # First 512 characters for classification
        return prediction[0]['label']

# Process files in the source directory
def process_files():
    categories = set()
    for file_name in os.listdir(SOURCE_DIR):
        file_path = os.path.join(SOURCE_DIR, file_name)
        _, ext = os.path.splitext(file_name)

        if ext.lower() in IMAGE_EXTENSIONS:
            category = classify_image(file_path)
        elif ext.lower() in PDF_EXTENSIONS:
            category = classify_pdf(file_path)
        else:
            print(f"Unsupported file type: {file_name}")
            continue

        # Track categories and move files
        categories.add(category)
        target_path = os.path.join(TARGET_DIR, category, file_name)
        
        # Ensure target directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        try:
            if MOVE_FILES:
                shutil.move(file_path, target_path)
                print(f"Moved {file_name} to {target_path}")
            else:
                shutil.copy(file_path, target_path)
                print(f"Copied {file_name} to {target_path}")
        except FileNotFoundError as e:
            print(f"Error moving/copying file {file_name}: {e}")

    # Ensure target directories exist
    ensure_directories(list(categories))

if __name__ == "__main__":
    ensure_directories(["Unknown"])
    process_files()
