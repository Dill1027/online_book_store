from models import Order, OrderCreate, utcnow


class OrderDataService:
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}

    def list_orders(self) -> list[Order]:
        return list(self._orders.values())

    def get_order_by_id(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def create_order(self, payload: OrderCreate) -> Order:
        if payload.orderId in self._orders:
            raise ValueError("Order with this orderId already exists")

        created = Order(**payload.model_dump())
        created.updatedAt = utcnow()
        self._orders[created.orderId] = created
        return created
