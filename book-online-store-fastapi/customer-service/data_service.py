from typing import List
from models import Customer, CustomerCreate, CustomerUpdate


class CustomerMockDataService:
    def __init__(self):
        self.customers: List[Customer] = [
            Customer(id=1, name="Kamal Perera", email="kamal@gmail.com", phone="0711111111", address="Colombo"),
            Customer(id=2, name="Nimal Silva", email="nimal@gmail.com", phone="0722222222", address="Kandy"),
        ]
        self.next_id = 3

    def get_all_customers(self):
        return self.customers

    def get_customer_by_id(self, customer_id: int):
        return next((customer for customer in self.customers if customer.id == customer_id), None)

    def get_customer_by_email(self, email: str):
        return next((customer for customer in self.customers if customer.email.lower() == email.lower()), None)

    def add_customer(self, customer_data: CustomerCreate):
        new_customer = Customer(id=self.next_id, **customer_data.model_dump())
        self.customers.append(new_customer)
        self.next_id += 1
        return new_customer

    def update_customer(self, customer_id: int, customer_data: CustomerUpdate):
        customer = self.get_customer_by_id(customer_id)
        if customer:
            update_data = customer_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(customer, key, value)
            return customer
        return None

    def delete_customer(self, customer_id: int):
        customer = self.get_customer_by_id(customer_id)
        if customer:
            self.customers.remove(customer)
            return True
        return False