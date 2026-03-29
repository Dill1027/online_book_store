import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx
import jwt
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="API Gateway", version="1.0.0")

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "60"))
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")

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


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXP_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    public_paths = {
        "/",
        "/auth/login",
        "/docs",
        "/openapi.json",
        "/redoc",
    }

    if request.url.path in public_paths:
        return await call_next(request)

    if request.url.path.startswith("/gateway"):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid Authorization header"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.replace("Bearer ", "", 1).strip()
        try:
            payload = decode_access_token(token)
            request.state.user = payload.get("sub")
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
                headers=exc.headers,
            )

    return await call_next(request)


async def forward_request(
    service: str,
    path: str,
    method: str,
    json_body: Optional[dict] = None,
    params: Optional[dict] = None
) -> Any:
    if service not in SERVICES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Service not found"},
        )

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
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"detail": f"Service unavailable: {str(exc)}"},
            )


@app.get("/")
def read_root():
    return {
        "message": "API Gateway is running",
        "available_services": list(SERVICES.keys())
    }


@app.post("/auth/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    if not AUTH_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gateway auth is not configured",
        )

    if (
        credentials.username != AUTH_USERNAME
        or credentials.password != AUTH_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(credentials.username)
    return TokenResponse(
        access_token=access_token,
        expires_in=JWT_EXP_MINUTES * 60,
    )


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


@app.get("/gateway/orders")
async def get_all_orders():
    return await forward_request("orders", "/api/orders", "GET")


@app.get("/gateway/orders/{order_id}")
async def get_order(order_id: int):
    return await forward_request("orders", f"/api/orders/{order_id}", "GET")


@app.post("/gateway/orders")
async def create_order(request: Request):
    body = await request.json()
    return await forward_request("orders", "/api/orders", "POST", json_body=body)


@app.put("/gateway/orders/{order_id}")
async def update_order(order_id: int, request: Request):
    body = await request.json()
    return await forward_request("orders", f"/api/orders/{order_id}", "PUT", json_body=body)


@app.delete("/gateway/orders/{order_id}")
async def delete_order(order_id: int):
    return await forward_request("orders", f"/api/orders/{order_id}", "DELETE")
