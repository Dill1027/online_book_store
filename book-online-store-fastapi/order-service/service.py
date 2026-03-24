from data_service import OrderDataService
from models import Order, OrderCreate


class OrderService:
    def __init__(self, data_service: OrderDataService) -> None:
        self.data_service = data_service

    def list_orders(self) -> list[Order]:
        return self.data_service.list_orders()

    def get_order_by_order_id(self, order_id: str) -> Order | None:
        return self.data_service.get_order_by_id(order_id)

    def create_order(self, payload: OrderCreate) -> Order:
        return self.data_service.create_order(payload)
