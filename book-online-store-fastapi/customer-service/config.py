import os

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://customer:12345@customer.r5ivplv.mongodb.net/",
)
DB_NAME = os.getenv("DB_NAME", "customer")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "customers")
