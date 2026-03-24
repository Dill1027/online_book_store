from fastapi import FastAPI, HTTPException, status

from data_service import CartDataService
from models import CartItem, CartItemCreate
from service import CartService

app = FastAPI(title="cart-service")

cart_service = CartService(CartDataService())


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "cart-service", "status": "ok"}


@app.get("/cart-items")
def list_cart_items() -> list[CartItem]:
    return cart_service.list_cart_items()


@app.get("/cart-items/{cart_id}")
def get_cart_item_by_cart_id(cart_id: str) -> CartItem:
    cart_item = cart_service.get_cart_item_by_cart_id(cart_id)
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    return cart_item


@app.post("/cart-items", status_code=status.HTTP_201_CREATED)
def create_cart_item(payload: CartItemCreate) -> CartItem:
    try:
        return cart_service.create_cart_item(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
