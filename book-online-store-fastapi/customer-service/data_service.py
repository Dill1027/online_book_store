import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
from models import Customer, CustomerCreate, CustomerUpdate

load_dotenv()


class CustomerMockDataService:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or MONGO_URI
        self.db_name = os.getenv("DB_NAME") or DB_NAME
        self.collection_name = os.getenv("COLLECTION_NAME") or COLLECTION_NAME

        if not self.mongo_uri or not self.db_name or not self.collection_name:
            raise ValueError("Missing MongoDB environment variables in .env file")

        self.client = None
        self.collection = None

    def _ensure_connected(self):
        """Lazy initialization of MongoDB connection"""
        if self.client is not None and self.collection is not None:
            return

        try:
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )

            # Test MongoDB connection
            self.client.admin.command("ping")

            self.collection = self.client[self.db_name][self.collection_name]

            # Make email unique
            self.collection.create_index("email", unique=True)
        except Exception as e:
            self.client = None
            self.collection = None
            raise Exception(f"Failed to connect to MongoDB: {str(e)}")

    def _to_customer(self, document):
        if not document:
            return None

        document = dict(document)
        document["id"] = str(document["_id"])
        document.pop("_id", None)

        return Customer(**document)

    def get_all_customers(self):
        self._ensure_connected()
        docs = self.collection.find({})
        return [self._to_customer(doc) for doc in docs]

    def get_customer_by_id(self, customer_id: str):
        try:
            self._ensure_connected()
            return self._to_customer(self.collection.find_one({"_id": ObjectId(customer_id)}))
        except:
            return None

    def get_customer_by_email(self, email: str):
        self._ensure_connected()
        return self._to_customer(self.collection.find_one({"email": email}))

    def add_customer(self, customer_data: CustomerCreate):
        self._ensure_connected()
        customer_dict = customer_data.model_dump()

        try:
            result = self.collection.insert_one(customer_dict)
        except DuplicateKeyError:
            raise ValueError("Email already exists")

        saved_customer = self.collection.find_one({"_id": result.inserted_id})
        return self._to_customer(saved_customer)

    def update_customer(self, customer_id: str, customer_data: CustomerUpdate):
        self._ensure_connected()
        update_data = customer_data.model_dump(exclude_unset=True)

        if not update_data:
            return self.get_customer_by_id(customer_id)

        try:
            result = self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": update_data}
            )
        except DuplicateKeyError:
            raise ValueError("Email already exists")
        except:
            return None

        if result.matched_count == 0:
            return None

        return self.get_customer_by_id(customer_id)

    def delete_customer(self, customer_id: str):
        try:
            self._ensure_connected()
            result = self.collection.delete_one({"_id": ObjectId(customer_id)})
            return result.deleted_count > 0
        except:
            return False