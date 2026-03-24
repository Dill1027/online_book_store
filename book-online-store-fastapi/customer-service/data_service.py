from models import Customer, CustomerCreate, utcnow


class CustomerDataService:
    def __init__(self) -> None:
        self._customers: dict[str, Customer] = {}

    def list_customers(self) -> list[Customer]:
        return list(self._customers.values())

    def get_customer_by_id(self, customer_id: str) -> Customer | None:
        return self._customers.get(customer_id)

    def create_customer(self, payload: CustomerCreate) -> Customer:
        if payload.customerId in self._customers:
            raise ValueError("Customer with this customerId already exists")

        created = Customer(**payload.model_dump())
        created.updatedAt = utcnow()
        self._customers[created.customerId] = created
        return created
