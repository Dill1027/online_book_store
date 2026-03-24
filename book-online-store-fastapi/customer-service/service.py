from data_service import CustomerMockDataService


class CustomerService:
    def __init__(self):
        self.data_service = CustomerMockDataService()

    def get_all(self):
        return self.data_service.get_all_customers()

    def get_by_id(self, customer_id: int):
        return self.data_service.get_customer_by_id(customer_id)

    def get_by_email(self, email: str):
        return self.data_service.get_customer_by_email(email)

    def create(self, customer_data):
        existing = self.get_by_email(customer_data.email)
        if existing:
            return None
        return self.data_service.add_customer(customer_data)

    def update(self, customer_id: int, customer_data):
        return self.data_service.update_customer(customer_id, customer_data)

    def delete(self, customer_id: int):
        return self.data_service.delete_customer(customer_id)