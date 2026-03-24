from data_service import CartDataService
from models import CartItem, CartItemCreate


class CartService:
    def __init__(self, data_service: CartDataService) -> None:
        self.data_service = data_service

    def list_cart_items(self) -> list[CartItem]:
        return self.data_service.list_cart_items()

    def get_cart_item_by_cart_id(self, cart_id: str) -> CartItem | None:
        return self.data_service.get_cart_item_by_id(cart_id)

    def create_cart_item(self, payload: CartItemCreate) -> CartItem:
        return self.data_service.create_cart_item(payload)
