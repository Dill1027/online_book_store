from datetime import date
from data_service import OrderMockDataService


class OrderService:
    def __init__(self):
        self.data_service = OrderMockDataService()

    def get_all(self):
        return self.data_service.get_all_orders()

    def get_by_id(self, order_id: int):
        return self.data_service.get_order_by_id(order_id)

    def calculate_total(self, items):
        return sum(item.quantity * item.price for item in items)

    def create(self, order_data):
        total_amount = self.calculate_total(order_data.items)
        order_date = date.today().isoformat()
        return self.data_service.add_order(order_data, total_amount, order_date)

    def update(self, order_id: int, order_data):
        existing_order = self.get_by_id(order_id)
        if not existing_order:
            return None

        total_amount = None
        if order_data.items is not None:
            total_amount = self.calculate_total(order_data.items)

        return self.data_service.update_order(order_id, order_data, total_amount)

    def delete(self, order_id: int):
        return self.data_service.delete_order(order_id)
