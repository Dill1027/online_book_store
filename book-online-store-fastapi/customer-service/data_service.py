import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from models import Customer, CustomerCreate, CustomerUpdate

load_dotenv()


class CustomerMockDataService:
    def __init__(self):
        mongo_uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("DB_NAME")
        collection_name = os.getenv("COLLECTION_NAME")

        if not mongo_uri or not db_name or not collection_name:
            raise ValueError("Missing MongoDB environment variables in .env file")

        self.client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )

        # Test MongoDB connection
        self.client.admin.command("ping")

        self.collection = self.client[db_name][collection_name]

        # Make email unique
        self.collection.create_index("email", unique=True)

    def _to_customer(self, document):
        if not document:
            return None

        document = dict(document)
        document["id"] = str(document["_id"])
        document.pop("_id", None)

        return Customer(**document)

    def get_all_customers(self):
        docs = self.collection.find({})
        return [self._to_customer(doc) for doc in docs]

    def get_customer_by_id(self, customer_id: str):
        try:
            return self._to_customer(self.collection.find_one({"_id": ObjectId(customer_id)}))
        except:
            return None

    def get_customer_by_email(self, email: str):
        return self._to_customer(self.collection.find_one({"email": email}))

    def add_customer(self, customer_data: CustomerCreate):
        customer_dict = customer_data.model_dump()

        try:
            result = self.collection.insert_one(customer_dict)
        except DuplicateKeyError:
            raise ValueError("Email already exists")

        saved_customer = self.collection.find_one({"_id": result.inserted_id})
        return self._to_customer(saved_customer)

    def update_customer(self, customer_id: str, customer_data: CustomerUpdate):
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
            result = self.collection.delete_one({"_id": ObjectId(customer_id)})
            return result.deleted_count > 0
        except:
            return False