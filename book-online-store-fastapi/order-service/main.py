from fastapi import FastAPI, HTTPException, status

from data_service import OrderDataService
from models import Order, OrderCreate
from service import OrderService

app = FastAPI(title="order-service")

order_service = OrderService(OrderDataService())


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "order-service", "status": "ok"}


@app.get("/orders")
def list_orders() -> list[Order]:
    return order_service.list_orders()


@app.get("/orders/{order_id}")
def get_order_by_order_id(order_id: str) -> Order:
    order = order_service.get_order_by_order_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate) -> Order:
    try:
        return order_service.create_order(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
