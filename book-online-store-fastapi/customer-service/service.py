from data_service import CustomerMockDataService
from models import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self):
        self.data_service = CustomerMockDataService()

    def get_all(self):
        return self.data_service.get_all_customers()

    def get_by_id(self, customer_id: str):
        return self.data_service.get_customer_by_id(customer_id)

    def get_by_email(self, email: str):
        return self.data_service.get_customer_by_email(email)

    def create(self, customer_data: CustomerCreate):
        existing_customer = self.get_by_email(customer_data.email)
        if existing_customer:
            raise ValueError("Email already exists")

        return self.data_service.add_customer(customer_data)

    def update(self, customer_id: str, customer_data: CustomerUpdate):
        existing_customer = self.get_by_id(customer_id)
        if not existing_customer:
            return None

        if customer_data.email and customer_data.email != existing_customer.email:
            email_owner = self.get_by_email(customer_data.email)
            if email_owner:
                raise ValueError("Email already exists")

        return self.data_service.update_customer(customer_id, customer_data)

    def delete(self, customer_id: str):
        return self.data_service.delete_customer(customer_id)