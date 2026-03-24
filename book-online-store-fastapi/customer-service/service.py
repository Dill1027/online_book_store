from data_service import CustomerDataService
from models import Customer, CustomerCreate


class CustomerService:
    def __init__(self, data_service: CustomerDataService) -> None:
        self.data_service = data_service

    def list_customers(self) -> list[Customer]:
        return self.data_service.list_customers()

    def get_customer_by_customer_id(self, customer_id: str) -> Customer | None:
        return self.data_service.get_customer_by_id(customer_id)

    def create_customer(self, payload: CustomerCreate) -> Customer:
        return self.data_service.create_customer(payload)
