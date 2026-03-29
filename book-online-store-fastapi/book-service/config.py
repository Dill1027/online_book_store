# book-service/config.py

import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://ramyamarappullige21_db_user:12345@cluster0.805wiu9.mongodb.net/bookstore")
DB_NAME = "bookstore"
COLLECTION_NAME = "books"
