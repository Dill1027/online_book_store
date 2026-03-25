from typing import Any, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from typing import List

# class Item(BaseModel):
#     model_config = ConfigDict(populate_by_name=True)
    
#     book_id: str = Field(validation_alias="bookId")
#     title: str
#     quantity: int
#     price: float

# class OrderCreate(BaseModel):
#     model_config = ConfigDict(populate_by_name=True)
    
#     customer_id: str = Field(validation_alias="customerId")
#     items: List[Item]
#     status: str = "Pending"
#     address: str

app = FastAPI(title="API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "books": "http://localhost:8001",
    "customers": "http://localhost:8002",
    "cart": "http://localhost:8003",
    "orders": "http://localhost:8004",
}


async def forward_request(
    service: str,
    path: str,
    method: str,
    json_body: Optional[dict] = None,
    params: Optional[dict] = None
) -> Any:
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    url = f"{SERVICES[service]}{path}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                json=json_body,
                params=params
            )

            try:
                content = response.json() if response.text else None
            except ValueError:
                content = {"message": response.text}

            return JSONResponse(content=content, status_code=response.status_code)

        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(exc)}")


@app.get("/")
def read_root():
    return {
        "message": "API Gateway is running",
        "available_services": list(SERVICES.keys())
    }


@app.get("/gateway/books")
async def get_all_books(request: Request):
    return await forward_request(
        "books",
        "/api/books",
        "GET",
        params=dict(request.query_params)
    )


@app.get("/gateway/books/{book_id}")
async def get_book(book_id: int):
    return await forward_request("books", f"/api/books/{book_id}", "GET")


@app.post("/gateway/books")
async def create_book(request: Request):
    body = await request.json()
    return await forward_request("books", "/api/books", "POST", json_body=body)


@app.put("/gateway/books/{book_id}")
async def update_book(book_id: int, request: Request):
    body = await request.json()
    return await forward_request("books", f"/api/books/{book_id}", "PUT", json_body=body)


@app.delete("/gateway/books/{book_id}")
async def delete_book(book_id: int):
    return await forward_request("books", f"/api/books/{book_id}", "DELETE")


@app.get("/gateway/customers")
async def get_all_customers():
    return await forward_request("customers", "/api/customers", "GET")


@app.get("/gateway/customers/{customer_id}")
async def get_customer(customer_id: int):
    return await forward_request("customers", f"/api/customers/{customer_id}", "GET")


@app.post("/gateway/customers")
async def create_customer(request: Request):
    body = await request.json()
    return await forward_request("customers", "/api/customers", "POST", json_body=body)


@app.put("/gateway/customers/{customer_id}")
async def update_customer(customer_id: int, request: Request):
    body = await request.json()
    return await forward_request("customers", f"/api/customers/{customer_id}", "PUT", json_body=body)


@app.delete("/gateway/customers/{customer_id}")
async def delete_customer(customer_id: int):
    return await forward_request("customers", f"/api/customers/{customer_id}", "DELETE")


@app.get("/gateway/cart")
async def get_all_cart_items():
    return await forward_request("cart", "/api/cart", "GET")


@app.get("/gateway/cart/{item_id}")
async def get_cart_item(item_id: int):
    return await forward_request("cart", f"/api/cart/{item_id}", "GET")


@app.get("/gateway/cart/customer/{customer_id}")
async def get_customer_cart(customer_id: int):
    return await forward_request("cart", f"/api/cart/customer/{customer_id}", "GET")


@app.post("/gateway/cart")
async def create_cart_item(request: Request):
    body = await request.json()
    return await forward_request("cart", "/api/cart", "POST", json_body=body)


@app.put("/gateway/cart/{item_id}")
async def update_cart_item(item_id: int, request: Request):
    body = await request.json()
    return await forward_request("cart", f"/api/cart/{item_id}", "PUT", json_body=body)


@app.delete("/gateway/cart/{item_id}")
async def delete_cart_item(item_id: int):
    return await forward_request("cart", f"/api/cart/{item_id}", "DELETE")


@app.delete("/gateway/cart/customer/{customer_id}")
async def clear_customer_cart(customer_id: int):
    return await forward_request("cart", f"/api/cart/customer/{customer_id}", "DELETE")



#   Order endpoints
@app.get("/gateway/orders")
async def get_all_orders():
    return await forward_request("orders", "/api/orders", "GET")


@app.get("/gateway/orders/{order_id}")
async def get_order(order_id: str):
    return await forward_request("orders", f"/api/orders/{order_id}", "GET")


@app.get("/gateway/orders/customer/{customer_id}")
async def get_customer_orders(customer_id: str):
    return await forward_request("orders", f"/api/orders/customer/{customer_id}", "GET")

@app.post("/gateway/orders")
async def create_order(request: Request):
    body = await request.json()
    return await forward_request( "orders", "/api/orders" "POST", json_body=body)
    
# @app.post("/gateway/orders")
# async def create_order(order: OrderCreate):
#     return await forward_request(
#         "orders",
#         "/api/orders",
#         "POST",
#         json_body=order.dict(by_alias=True)
#     )

@app.put("/gateway/orders/{order_id}")
async def update_order(order_id: str, request: Request):
    body = await request.json()
    return await forward_request( "orders", f"/api/orders/{order_id}", "PUT",json_body=body)

    
# @app.put("/gateway/orders/{order_id}")
# async def update_order(order_id: str, order: OrderCreate):
#     return await forward_request(
#         "orders",
#         f"/api/orders/{order_id}",
#         "PUT",
#         json_body=order.dict(by_alias=True)
#     )


@app.delete("/gateway/orders/{order_id}")
async def delete_order(order_id: str):
    return await forward_request("orders", f"/api/orders/{order_id}", "DELETE")
