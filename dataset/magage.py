import os
import json
from urllib.parse import quote

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
