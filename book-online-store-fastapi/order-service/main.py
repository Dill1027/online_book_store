from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from models import Order, OrderCreate, OrderUpdate
from service import OrderService

app = FastAPI(title="Order Microservice", version="1.0.0")

# Initialize service
order_service = OrderService()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"message": "Order Microservice is running"}


@app.get("/api/orders", response_model=List[Order])
def get_all_orders():
    """Get all orders"""
    return order_service.get_all()


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    """Get an order by ID"""
    order = order_service.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate):
    """Create a new order"""
    return order_service.create(order)


@app.put("/api/orders/{order_id}", response_model=Order)
def update_order(order_id: int, order: OrderUpdate):
    """Update an order"""
    updated_order = order_service.update(order_id, order)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order


@app.delete("/api/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int):
    """Delete an order"""
    success = order_service.delete(order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return None