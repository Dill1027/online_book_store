import os

# Support both variable names used in different branches/configs.
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv(
    "MONGO_URI",
    "mongodb+srv://customer:12345@customer.r5ivplv.mongodb.net/?retryWrites=true&w=majority",
)
DB_NAME = os.getenv("DB_NAME", "customer")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "customers")
