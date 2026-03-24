import os

from pymongo import MongoClient

from models import Customer, CustomerCreate, CustomerUpdate


class CustomerMockDataService:
    def __init__(self):
        mongo_uri = os.getenv(
            "MONGODB_URI",
            "mongodb+srv://smartlearn:1234@cluster0.9ypskee.mongodb.net/smartlearn"
        )
        self.client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=3000
        )
        self.collection = self.client["smartlearn"]["customers"]

    @staticmethod
    def _to_customer(document: dict | None) -> Customer | None:
        if not document:
            return None
        document.pop("_id", None)
        return Customer(**document)

    def _next_id(self) -> int:
        latest = self.collection.find_one(sort=[("id", -1)])
        if not latest:
            return 1
        return int(latest.get("id", 0)) + 1

    def get_all_customers(self):
        docs = self.collection.find({})
        return [self._to_customer(doc) for doc in docs]

    def get_customer_by_id(self, customer_id: int):
        return self._to_customer(self.collection.find_one({"id": customer_id}))

    def get_customer_by_email(self, email: str):
        return self._to_customer(self.collection.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}}))

    def add_customer(self, customer_data: CustomerCreate):
        new_customer = Customer(id=self._next_id(), **customer_data.model_dump())
        self.collection.insert_one(new_customer.model_dump())
        return new_customer

    def update_customer(self, customer_id: int, customer_data: CustomerUpdate):
        update_data = customer_data.model_dump(exclude_unset=True)
        if not update_data:
            return self.get_customer_by_id(customer_id)

        result = self.collection.update_one({"id": customer_id}, {"$set": update_data})
        if result.matched_count == 0:
            return None
        return self.get_customer_by_id(customer_id)

    def delete_customer(self, customer_id: int):
        result = self.collection.delete_one({"id": customer_id})
        return result.deleted_count > 0
