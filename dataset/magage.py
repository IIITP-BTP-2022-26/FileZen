import os
import requests
import json
from urllib.parse import quote

# Google Custom Search API Setup
API_KEY = "AIzaSyAS7lN3Z4lIUVzQ98lcoekdtUQapMF_5tg"  # Replace with your Google API Key
CX = "9316075300e024cd1"  # Replace with your Custom Search Engine ID

# Category map
category_map = {
    "Documents": "documents, driving licence, pan card, id proof",
    "Receipts_Slips": "Receipt Slip",
    "Family_Freinds": "family, parents",
    "Friends": "friends, school friends, college friends, work friends",
    "Nature": "raw nature photos",
    "Pets_Animals": "animals, pets raw images",
    "Recepie_Food": "food, recipes, cooking",
    "Travel": "travel, vacation, adventures",
    "Selfies": "raw selfie",
    "Artwork_Designs": "artwork, designs, paintings, sculptures",
    "Screenshots": "screenshot examples",
    "Memes": "memes, funny, humor",
    "Sports": "sports, athletes, games",
    "Events": "events, parties, celebrations raw images",
    "Study_Material": "study material, books, notes, educational resources",
    "Wallpapers": "wallpapers, backgrounds, phone wallpapers",
}

# Path to save images
dataset_dir = "D:/workspace/python/folder_manager/dataset/images"
os.makedirs(dataset_dir, exist_ok=True)

# Google Search API URL
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

# Function to download images for each category
def download_images_for_category(category_name, search_terms, num_images=10):
    category_dir = os.path.join(dataset_dir, category_name)
    os.makedirs(category_dir, exist_ok=True)
    
    # Prepare the search query
    query = quote(search_terms)  # URL encode the search query
    params = {
        "key": API_KEY,
        "cx": CX,
        "searchType": "image",
        "q": query,
        "num": num_images
    }
    
    # Send request to Google Custom Search API
    response = requests.get(SEARCH_URL, params=params)
    
    # Check if the response is successful
    if response.status_code == 200:
        search_results = response.json()
        if "items" in search_results:
            # Loop through the results and download the images
            for i, item in enumerate(search_results["items"]):
                image_url = item["link"]
                img_data = requests.get(image_url).content
                file_name = os.path.basename(image_url).split("?")[0]
                img_path = os.path.join(category_dir, f"{file_name}_{category_name}_{i+1}.jpg")
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                print(f"Downloaded {img_path}")
        else:
            print(f"No results found for {category_name}.")
    else:
        print(f"Error occurred while fetching images for {category_name}: {response.status_code}")

# Download images for all categories
for category_name, search_terms in category_map.items():
    print(f"Downloading images for {category_name}...")
    download_images_for_category(category_name, search_terms)

print("Image download completed.")
