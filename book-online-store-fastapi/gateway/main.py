import os

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="api-gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

BOOK_SERVICE_URL = os.getenv("BOOK_SERVICE_URL", "http://127.0.0.1:8001")
CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL", "http://127.0.0.1:8002")
CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://127.0.0.1:8003")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://127.0.0.1:8004")

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


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "api-gateway", "status": "ok"}


@app.get("/api/services")
def list_services() -> dict[str, str]:
    return {
        "books": BOOK_SERVICE_URL,
        "customers": CUSTOMER_SERVICE_URL,
        "cartItems": CART_SERVICE_URL,
        "orders": ORDER_SERVICE_URL
    }


async def forward_request(request: Request, target_base: str, path_suffix: str) -> Response:
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


@app.api_route("/api/books", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.api_route("/api/books/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_books(request: Request, path: str = "") -> Response:
    suffix = f"/books/{path}" if path else "/books"
    return await forward_request(request, BOOK_SERVICE_URL, suffix)


@app.api_route("/api/customers", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.api_route("/api/customers/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_customers(request: Request, path: str = "") -> Response:
    suffix = f"/customers/{path}" if path else "/customers"
    return await forward_request(request, CUSTOMER_SERVICE_URL, suffix)


@app.api_route("/api/cart-items", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.api_route("/api/cart-items/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_cart_items(request: Request, path: str = "") -> Response:
    suffix = f"/cart-items/{path}" if path else "/cart-items"
    return await forward_request(request, CART_SERVICE_URL, suffix)


@app.api_route("/api/orders", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.api_route("/api/orders/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_orders(request: Request, path: str = "") -> Response:
    suffix = f"/orders/{path}" if path else "/orders"
    return await forward_request(request, ORDER_SERVICE_URL, suffix)
