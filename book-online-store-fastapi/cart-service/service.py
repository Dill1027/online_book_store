from data_service import CartMockDataService


class CartService:
    def __init__(self):
        self.data_service = CartMockDataService()

    def get_all(self):
        return self.data_service.get_all_cart_items()

    def get_by_id(self, item_id: int):
        return self.data_service.get_cart_item_by_id(item_id)

    def get_by_customer_id(self, customer_id: int):
        return self.data_service.get_cart_items_by_customer_id(customer_id)

    def create(self, item_data):
        return self.data_service.add_cart_item(item_data)

    def update(self, item_id: int, item_data):
        return self.data_service.update_cart_item(item_id, item_data)

    def delete(self, item_id: int):
        return self.data_service.delete_cart_item(item_id)

    def clear_customer_cart(self, customer_id: int):
        return self.data_service.clear_customer_cart(customer_id)
