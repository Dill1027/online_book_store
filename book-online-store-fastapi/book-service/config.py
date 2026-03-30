import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://ramyamarappullige21_db_user:12345@cluster0.805wiu9.mongodb.net/bookstore?retryWrites=true&w=majority&ssl=true",
)
DB_NAME = os.getenv("DB_NAME", "bookstore")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "books")
