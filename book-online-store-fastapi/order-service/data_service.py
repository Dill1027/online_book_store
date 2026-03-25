import os
from typing import Optional
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from models import Order, OrderCreate, OrderUpdate

load_dotenv()

class OrderMockDataService:
    def __init__(self):
        mongo_uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("DB_NAME")
        collection_name = os.getenv("COLLECTION_NAME")

        self.client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=3000
        )

        self.collection = self.client[db_name][collection_name]

    def _to_order(self, document):
        if not document:
            return None

        document = dict(document)
        document["id"] = str(document["_id"]) 
        document.pop("_id", None)

        return Order(**document)


    def get_all_orders(self):
        docs = self.collection.find({})
        return [self._to_order(doc) for doc in docs]

    def get_order_by_id(self, order_id: str):
        try:
            return self._to_order(self.collection.find_one({"_id": ObjectId(order_id)}))
        except:
            return None

    def get_orders_by_customer_id(self, customer_id: str):
        docs = self.collection.find({"customer_id": customer_id})
        return [self._to_order(doc) for doc in docs]

    def add_order(self, order_data: OrderCreate, total_amount: float, order_date: str, address: str):
        order_dict = order_data.model_dump()

        order_dict["total_amount"] = total_amount
        order_dict["order_date"] = order_date
        order_dict["address"] = address

        result = self.collection.insert_one(order_dict)

        saved_order = self.collection.find_one({"_id": result.inserted_id})

        return self._to_order(saved_order)



    def update_order(self, order_id: str, order_data: OrderUpdate, total_amount: Optional[float] = None):
        update_data = order_data.model_dump(exclude_unset=True)

        if total_amount is not None:
            update_data["total_amount"] = total_amount

        if not update_data:
            return self.get_order_by_id(order_id)

        try:
            result = self.collection.update_one({"_id": ObjectId(order_id)}, {"$set": update_data})
        except:
            return None

        if result.matched_count == 0:
            return None

        return self.get_order_by_id(order_id)

    def delete_order(self, order_id: str):
        try:
            result = self.collection.delete_one({"_id": ObjectId(order_id)})
            return result.deleted_count > 0
        except:
            return False