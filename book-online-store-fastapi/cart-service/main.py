from typing import List

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from data_service import DataStoreUnavailableError
from models import CartItem, CartItemCreate, CartItemUpdate
from service import CartService

app = FastAPI(title="Cart Service", version="1.0.0")
cart_service = CartService()
NOT_FOUND_DETAIL = "Cart item not found"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DataStoreUnavailableError)
async def datastore_unavailable_handler(request: Request, exc: DataStoreUnavailableError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Cart datastore is unavailable"},
    )


@app.get("/")
def read_root():
    return {"message": "Cart Service is running"}


@app.get("/health")
def health_check():
    if cart_service.ping():
        return {"status": "ok", "datastore": "up"}
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "degraded", "datastore": "down", "detail": "Cart datastore is unavailable"},
    )


@app.get("/api/cart", response_model=List[CartItem])
def get_all_cart_items():
    return cart_service.get_all()


@app.get(
    "/api/cart/{item_id}",
    response_model=CartItem,
    responses={404: {"description": "Cart item not found"}},
)
def get_cart_item(item_id: int):
    item = cart_service.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=NOT_FOUND_DETAIL)
    return item


@app.get("/api/cart/customer/{customer_id}", response_model=List[CartItem])
def get_customer_cart(customer_id: int):
    return cart_service.get_by_customer_id(customer_id)


@app.post("/api/cart", response_model=CartItem, status_code=status.HTTP_201_CREATED)
def create_cart_item(item: CartItemCreate):
    return cart_service.create(item)


@app.put(
    "/api/cart/{item_id}",
    response_model=CartItem,
    responses={404: {"description": "Cart item not found"}},
)
def update_cart_item(item_id: int, item: CartItemUpdate):
    updated_item = cart_service.update(item_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail=NOT_FOUND_DETAIL)
    return updated_item


@app.delete(
    "/api/cart/{item_id}",
    responses={404: {"description": "Cart item not found"}},
)
def delete_cart_item(item_id: int):
    success = cart_service.delete(item_id)
    if not success:
        raise HTTPException(status_code=404, detail=NOT_FOUND_DETAIL)
    return {"message": "Cart item deleted successfully"}


@app.delete("/api/cart/customer/{customer_id}")
def clear_customer_cart(customer_id: int):
    removed_count = cart_service.clear_customer_cart(customer_id)
    return {
        "message": "Customer cart cleared successfully",
        "removed_count": removed_count,
    }
