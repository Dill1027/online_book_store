from models import CartItem, CartItemCreate, utcnow


class CartDataService:
    def __init__(self) -> None:
        self._cart_items: dict[str, CartItem] = {}

    def list_cart_items(self) -> list[CartItem]:
        return list(self._cart_items.values())

    def get_cart_item_by_id(self, cart_id: str) -> CartItem | None:
        return self._cart_items.get(cart_id)

    def create_cart_item(self, payload: CartItemCreate) -> CartItem:
        if payload.cartId in self._cart_items:
            raise ValueError("Cart item with this cartId already exists")

        created = CartItem(**payload.model_dump())
        created.updatedAt = utcnow()
        self._cart_items[created.cartId] = created
        return created
