from typing import List
from models import CartItem, CartItemCreate, CartItemUpdate


class CartMockDataService:
    def __init__(self):
        self.cart_items: List[CartItem] = [
            CartItem(id=1, customer_id=1, book_id=1, quantity=2),
            CartItem(id=2, customer_id=1, book_id=2, quantity=1),
        ]
        self.next_id = 3

    def get_all_cart_items(self):
        return self.cart_items

    def get_cart_item_by_id(self, item_id: int):
        return next((item for item in self.cart_items if item.id == item_id), None)

    def get_cart_items_by_customer_id(self, customer_id: int):
        return [item for item in self.cart_items if item.customer_id == customer_id]

    def add_cart_item(self, item_data: CartItemCreate):
        new_item = CartItem(id=self.next_id, **item_data.model_dump())
        self.cart_items.append(new_item)
        self.next_id += 1
        return new_item

    def update_cart_item(self, item_id: int, item_data: CartItemUpdate):
        item = self.get_cart_item_by_id(item_id)
        if item:
            update_data = item_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(item, key, value)
            return item
        return None

    def delete_cart_item(self, item_id: int):
        item = self.get_cart_item_by_id(item_id)
        if item:
            self.cart_items.remove(item)
            return True
        return False

    def clear_customer_cart(self, customer_id: int):
        original_count = len(self.cart_items)
        self.cart_items = [item for item in self.cart_items if item.customer_id != customer_id]
        return original_count - len(self.cart_items)
