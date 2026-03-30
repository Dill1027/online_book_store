# gateway/main.py

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Any

app = FastAPI(title="API Gateway", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Service URLs
SERVICES = {
    "book": "http://localhost:8001"   # your Book Service port
}

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
    "host"
}


@app.get("/")
def read_root():
    return {
        "message": "API Gateway is running",
        "available_services": list(SERVICES.keys())
    }


async def forward_request(request: Request, target_base: str, path_suffix: str) -> Response:
    """Forward HTTP request to microservice"""
    forward_path = path_suffix if path_suffix else ""
    target_url = f"{target_base}{forward_path}"

    filtered_headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

    body = await request.body()

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            upstream = await client.request(
                method=request.method,
                url=target_url,
                params=request.query_params,
                headers=filtered_headers,
                content=body
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {exc}") from exc

    response_headers = {
        key: value
        for key, value in upstream.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }
    return Response(content=upstream.content, status_code=upstream.status_code, headers=response_headers)


# 📖 Book Service Routes

@app.api_route("/api/books", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.api_route("/api/books/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_books(request: Request, path: str = "") -> Response:
    suffix = f"/books/{path}" if path else "/books"
    return await forward_request(request, SERVICES["book"], suffix)


@app.api_route("/api/customers", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.api_route("/api/customers/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_customers(request: Request, path: str = "") -> Response:
    suffix = f"/customers/{path}" if path else "/customers"
    return await forward_request(request, SERVICES.get("customer", "http://localhost:8002"), suffix)


@app.api_route("/api/cart-items", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.api_route("/api/cart-items/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_cart_items(request: Request, path: str = "") -> Response:
    suffix = f"/cart-items/{path}" if path else "/cart-items"
    return await forward_request(request, SERVICES.get("cart", "http://localhost:8003"), suffix)


@app.api_route("/api/orders", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.api_route("/api/orders/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_orders(request: Request, path: str = "") -> Response:
    suffix = f"/orders/{path}" if path else "/orders"
    return await forward_request(request, SERVICES.get("order", "http://localhost:8004"), suffix)
    try:
        body = await request.json()
    except json.JSONDecodeError as exc:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(f"[{request_id}] Invalid JSON in request body: {str(exc)}")
        raise ValidationError("body", f"Invalid JSON: {str(exc)}")
    return await forward_request("books", f"/api/books/{book_id}", "PUT", json_body=body, request=request)


@app.delete("/gateway/books/{book_id}", dependencies=[Depends(get_current_user)])
async def delete_book(book_id: int, request: Request):
    return await forward_request("books", f"/api/books/{book_id}", "DELETE", request=request)


@app.get("/gateway/customers", dependencies=[Depends(get_current_user)])
async def get_all_customers(request: Request):
    return await forward_request("customers", "/api/customers", "GET", request=request)


@app.get("/gateway/customers/{customer_id}", dependencies=[Depends(get_current_user)])
async def get_customer(customer_id: int, request: Request):
    return await forward_request("customers", f"/api/customers/{customer_id}", "GET", request=request)


@app.post("/gateway/customers", dependencies=[Depends(get_current_user)])
async def create_customer(request: Request):
    try:
        body = await request.json()
    except json.JSONDecodeError as exc:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(f"[{request_id}] Invalid JSON in request body: {str(exc)}")
        raise ValidationError("body", f"Invalid JSON: {str(exc)}")
    return await forward_request("customers", "/api/customers", "POST", json_body=body, request=request)


@app.put("/gateway/customers/{customer_id}", dependencies=[Depends(get_current_user)])
async def update_customer(customer_id: int, request: Request):
    try:
        body = await request.json()
    except json.JSONDecodeError as exc:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(f"[{request_id}] Invalid JSON in request body: {str(exc)}")
        raise ValidationError("body", f"Invalid JSON: {str(exc)}")
    return await forward_request("customers", f"/api/customers/{customer_id}", "PUT", json_body=body, request=request)


@app.delete("/gateway/customers/{customer_id}", dependencies=[Depends(get_current_user)])
async def delete_customer(customer_id: int, request: Request):
    return await forward_request("customers", f"/api/customers/{customer_id}", "DELETE", request=request)


@app.get("/gateway/cart", dependencies=[Depends(get_current_user)])
async def get_all_cart_items(request: Request):
    return await forward_request("cart", "/api/cart", "GET", request=request)


@app.get("/gateway/cart/health", dependencies=[Depends(get_current_user)])
async def get_cart_health(request: Request):
    return await forward_request("cart", "/health", "GET", request=request)


@app.get("/gateway/cart/{item_id}", dependencies=[Depends(get_current_user)])
async def get_cart_item(item_id: int, request: Request):
    return await forward_request("cart", f"/api/cart/{item_id}", "GET", request=request)


@app.get("/gateway/cart/customer/{customer_id}", dependencies=[Depends(get_current_user)])
async def get_customer_cart(customer_id: int, request: Request):
    return await forward_request("cart", f"/api/cart/customer/{customer_id}", "GET", request=request)


@app.post("/gateway/cart", dependencies=[Depends(get_current_user)])
async def create_cart_item(request: Request):
    try:
        body = await request.json()
    except json.JSONDecodeError as exc:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(f"[{request_id}] Invalid JSON in request body: {str(exc)}")
        raise ValidationError("body", f"Invalid JSON: {str(exc)}")
    return await forward_request("cart", "/api/cart", "POST", json_body=body, request=request)


@app.put("/gateway/cart/{item_id}", dependencies=[Depends(get_current_user)])
async def update_cart_item(item_id: int, request: Request):
    try:
        body = await request.json()
    except json.JSONDecodeError as exc:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(f"[{request_id}] Invalid JSON in request body: {str(exc)}")
        raise ValidationError("body", f"Invalid JSON: {str(exc)}")
    return await forward_request("cart", f"/api/cart/{item_id}", "PUT", json_body=body, request=request)


@app.delete("/gateway/cart/{item_id}", dependencies=[Depends(get_current_user)])
async def delete_cart_item(item_id: int, request: Request):
    return await forward_request("cart", f"/api/cart/{item_id}", "DELETE", request=request)


@app.delete("/gateway/cart/customer/{customer_id}", dependencies=[Depends(get_current_user)])
async def clear_customer_cart(customer_id: int, request: Request):
    return await forward_request("cart", f"/api/cart/customer/{customer_id}", "DELETE", request=request)


@app.get("/gateway/orders", dependencies=[Depends(get_current_user)])
async def get_all_orders(request: Request):
    return await forward_request("orders", "/api/orders", "GET", request=request)


@app.get("/gateway/orders/{order_id}", dependencies=[Depends(get_current_user)])
async def get_order(order_id: str, request: Request):
    return await forward_request("orders", f"/api/orders/{order_id}", "GET", request=request)


@app.get("/gateway/orders/customer/{customer_id}", dependencies=[Depends(get_current_user)])
async def get_customer_orders(customer_id: str, request: Request):
    return await forward_request("orders", f"/api/orders/customer/{customer_id}", "GET", request=request)

@app.post("/gateway/orders", dependencies=[Depends(get_current_user)])
async def create_order(request: Request):
    try:
        body = await request.json()
    except json.JSONDecodeError as exc:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(f"[{request_id}] Invalid JSON in request body: {str(exc)}")
        raise ValidationError("body", f"Invalid JSON: {str(exc)}")
    return await forward_request("orders", "/api/orders", "POST", json_body=body, request=request)

@app.put("/gateway/orders/{order_id}", dependencies=[Depends(get_current_user)])
async def update_order(order_id: str, request: Request):
    try:
        body = await request.json()
    except json.JSONDecodeError as exc:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(f"[{request_id}] Invalid JSON in request body: {str(exc)}")
        raise ValidationError("body", f"Invalid JSON: {str(exc)}")
    return await forward_request("orders", f"/api/orders/{order_id}", "PUT", json_body=body, request=request)


@app.delete("/gateway/orders/{order_id}", dependencies=[Depends(get_current_user)])
async def delete_order(order_id: str, request: Request):
    return await forward_request("orders", f"/api/orders/{order_id}", "DELETE", request=request)
