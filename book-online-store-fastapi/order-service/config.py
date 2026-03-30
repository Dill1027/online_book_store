import os

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://jsdilshani1_db_user:12345@cluster0.4zkconi.mongodb.net/",
)
DB_NAME = os.getenv("DB_NAME", "order")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "orders")
