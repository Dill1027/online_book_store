import os
import logging
import json
import time
import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Optional

import httpx
import jwt
from fastapi import Body, Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field


# Error Response Models
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    request_id: str
    status_code: int
    timestamp: str
    error: ErrorDetail
    path: str
    method: str


# Custom Exceptions
class GatewayException(Exception):
    """Base exception for gateway errors"""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        details: Optional[dict] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ServiceNotFoundError(GatewayException):
    """Raised when a service is not registered"""

    def __init__(self, service: str):
        super().__init__(
            code="SERVICE_NOT_FOUND",
            message=f"Service '{service}' is not registered in the gateway",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"service": service},
        )


class ServiceUnavailableError(GatewayException):
    """Raised when a service is unavailable"""

    def __init__(self, service: str, reason: str):
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            message=f"Service '{service}' is currently unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": service, "reason": reason},
        )


class AuthenticationError(GatewayException):
    """Raised when authentication fails"""

    def __init__(self, reason: str):
        super().__init__(
            code="AUTHENTICATION_FAILED",
            message=f"Authentication failed: {reason}",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details={"reason": reason},
        )


class ValidationError(GatewayException):
    """Raised when request validation fails"""

    def __init__(self, field: str, reason: str):
        super().__init__(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"field": field, "reason": reason},
        )


class InternalServerError(GatewayException):
    """Raised for internal server errors"""

    def __init__(self, reason: str):
        super().__init__(
            code="INTERNAL_SERVER_ERROR",
            message="An internal server error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"reason": reason},
        )


app = FastAPI(title="API Gateway", version="1.0.0")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("api-gateway")

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "60"))
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
_auth_password = os.getenv("AUTH_PASSWORD")
if _auth_password and _auth_password.strip():
    AUTH_PASSWORD = _auth_password.strip()
else:
    AUTH_PASSWORD = AUTH_USERNAME
    logger.warning(
        "AUTH_PASSWORD is not configured; using AUTH_USERNAME as a development fallback"
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers
@app.exception_handler(GatewayException)
async def gateway_exception_handler(request: Request, exc: GatewayException):
    request_id = getattr(request.state, "request_id", "unknown")

    error_response = ErrorResponse(
        request_id=request_id,
        status_code=exc.status_code,
        timestamp=datetime.now(timezone.utc).isoformat(),
        error=ErrorDetail(code=exc.code, message=exc.message, details=exc.details),
        path=request.url.path,
        method=request.method,
    )

    log_level = "warning" if exc.status_code < 500 else "error"
    getattr(logger, log_level)(
        f"[{request_id}] GATEWAY ERROR | "
        f"Code: {exc.code} | "
        f"Status: {exc.status_code} | "
        f"Message: {exc.message}"
    )

    return JSONResponse(
        status_code=exc.status_code, content=error_response.dict()
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    request_id = getattr(request.state, "request_id", "unknown")

    error_response = ErrorResponse(
        request_id=request_id,
        status_code=status.HTTP_400_BAD_REQUEST,
        timestamp=datetime.now(timezone.utc).isoformat(),
        error=ErrorDetail(
            code="VALUE_ERROR",
            message="Invalid request data",
            details={"error": str(exc)},
        ),
        path=request.url.path,
        method=request.method,
    )

    logger.warning(f"[{request_id}] VALUE ERROR | {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content=error_response.dict()
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")

    error_response = ErrorResponse(
        request_id=request_id,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        timestamp=datetime.now(timezone.utc).isoformat(),
        error=ErrorDetail(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details={"error_type": type(exc).__name__},
        ),
        path=request.url.path,
        method=request.method,
    )

    logger.error(f"[{request_id}] UNHANDLED EXCEPTION | {type(exc).__name__}: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict(),
    )



@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()
    request_body = None

    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            request_body = await request.body()

            async def receive():
                await asyncio.sleep(0)
                return {
                    "type": "http.request",
                    "body": request_body,
                    "more_body": False,
                }

            request._receive = receive
        except Exception:
            pass

    logger.info(
        f"[{request_id}] INCOMING REQUEST | "
        f"Method: {request.method} | "
        f"Path: {request.url.path} | "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )

    if request_body:
        try:
            body_str = request_body.decode("utf-8")
            logger.debug(f"[{request_id}] REQUEST BODY | {body_str}")
        except Exception:
            logger.debug(f"[{request_id}] REQUEST BODY | (binary or decode error)")

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        f"[{request_id}] OUTGOING RESPONSE | "
        f"Status: {response.status_code} | "
        f"Duration: {process_time:.3f}s"
    )

    return response

ORDER_SERVICE_DEFAULT_URL = "http://localhost:8004"

SERVICES = {
    "books": os.getenv("BOOK_SERVICE_URL", "http://localhost:8001"),
    "cart": os.getenv("CART_SERVICE_URL", "http://localhost:8002"),
    "customers": os.getenv("CUSTOMER_SERVICE_URL", "http://localhost:8003"),
    "orders": os.getenv("ORDER_SERVICE_URL", "http://localhost:8004"),
}

BODY_METHODS = {"POST", "PUT", "PATCH"}
EXAMPLE_BOOK_TITLE = "FastAPI Essentials"
REQUIRED_UPDATE_BODY_MESSAGE = "Request body is required. Provide at least one field in JSON."
EMPTY_UPDATE_BODY_MESSAGE = "Request body cannot be empty. Provide at least one field to update."


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class BookCreateRequest(BaseModel):
    title: str
    author: str
    price: float = Field(..., ge=0)
    category: str
    stock: int = Field(..., ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "title": EXAMPLE_BOOK_TITLE,
                "author": "Robert C. Martin",
                "price": 42.5,
                "category": "Programming",
                "stock": 10,
            }
        }


class BookUpdateRequest(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    category: Optional[str] = None
    stock: Optional[int] = Field(default=None, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "price": 39.99,
                "stock": 7,
            }
        }


class CustomerCreateRequest(BaseModel):
    name: str
    email: str
    phone: str
    address: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "0712345678",
                "address": "Colombo",
            }
        }


class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "0770001111",
                "address": "Kandy",
            }
        }


class CartItemCreateRequest(BaseModel):
    customer_id: int
    book_id: str
    book_title: Optional[str] = None
    quantity: int = Field(..., gt=0)
    price: Optional[float] = Field(default=None, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": 1,
                "book_id": "BK-1001",
                "book_title": EXAMPLE_BOOK_TITLE,
                "quantity": 2,
                "price": 19.99,
            }
        }


class CartItemUpdate(BaseModel):
    book_id: Optional[str] = Field(default=None, description="Book identifier")
    book_title: Optional[str] = Field(default=None, description="Book title")
    quantity: Optional[int] = Field(default=None, gt=0, description="Quantity to set")
    price: Optional[float] = Field(default=None, ge=0, description="Unit price")

    class Config:
        json_schema_extra = {
            "example": {
                "book_id": "BK-1001",
                "book_title": EXAMPLE_BOOK_TITLE,
                "quantity": 2,
                "price": 19.99,
            }
        }


class OrderItemRequest(BaseModel):
    book_id: str
    title: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., ge=0)


class OrderCreateRequest(BaseModel):
    customer_id: str
    items: list[OrderItemRequest]
    status: Optional[str] = "Pending"
    address: str

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "1",
                "items": [
                    {
                        "book_id": "BK-1001",
                        "title": EXAMPLE_BOOK_TITLE,
                        "quantity": 2,
                        "price": 19.99,
                    }
                ],
                "status": "Pending",
                "address": "Colombo",
            }
        }


class OrderUpdateRequest(BaseModel):
    customer_id: Optional[str] = None
    items: Optional[list[OrderItemRequest]] = None
    status: Optional[str] = None
    address: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "Shipped",
            }
        }


security = HTTPBearer()


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
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid or malformed token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    return decode_access_token(token)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    request_id = getattr(request.state, "request_id", "unknown")
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
        auth_header = request.headers.get("Authorization", "").strip()

        if not auth_header:
            logger.warning(
                f"[{request_id}] Authorization attempt without header | Path: {request.url.path}"
            )
            raise AuthenticationError("Missing Authorization header")

        if not auth_header.startswith("Bearer "):
            logger.warning(
                f"[{request_id}] Invalid Authorization header format | Path: {request.url.path}"
            )
            raise AuthenticationError("Invalid Authorization header format. Expected: Bearer <token>")

        token = auth_header.replace("Bearer ", "", 1).strip()

        if not token:
            logger.warning(
                f"[{request_id}] Empty token provided | Path: {request.url.path}"
            )
            raise AuthenticationError("Token is empty")

        try:
            payload = decode_access_token(token)
            request.state.user = payload.get("sub")
            logger.debug(
                f"[{request_id}] Authentication successful | User: {request.state.user}"
            )
        except GatewayException:
            raise
        except Exception as exc:
            logger.error(
                f"[{request_id}] Unexpected error during token validation: {str(exc)}"
            )
            raise AuthenticationError(f"Token validation failed: {str(exc)}")

    return await call_next(request)


async def forward_request(
    service: str,
    path: str,
    method: str,
    json_body: Optional[dict] = None,
    params: Optional[dict] = None,
    request: Optional[Request] = None,
) -> Any:
    request_id = getattr(request.state, "request_id", "unknown") if request and hasattr(request, "state") else "unknown"

    if service not in SERVICES:
        logger.error(f"[{request_id}] Attempted access to unregistered service: {service}")
        raise ServiceNotFoundError(service)

    url = f"{SERVICES[service]}{path}"
    logger.debug(
        f"[{request_id}] Forwarding {method} request to {service} | URL: {url}"
    )

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                json=json_body,
                params=params,
            )

            if response.status_code == status.HTTP_204_NO_CONTENT or not response.content:
                return Response(status_code=response.status_code)

            try:
                content = response.json() if response.text else None
            except json.JSONDecodeError as exc:
                logger.warning(
                    f"[{request_id}] Failed to parse JSON response from {service}: {str(exc)}"
                )
                content = {"message": response.text}

            logger.debug(
                f"[{request_id}] Received response from {service} | Status: {response.status_code}"
            )

            return JSONResponse(content=content, status_code=response.status_code)

        except httpx.ConnectError as exc:
            logger.error(
                f"[{request_id}] Connection error to {service} ({url}): {str(exc)}"
            )
            raise ServiceUnavailableError(service, f"Connection failed: {str(exc)}")

        except httpx.TimeoutException as exc:
            logger.error(
                f"[{request_id}] Timeout connecting to {service} ({url}): {str(exc)}"
            )
            raise ServiceUnavailableError(service, f"Request timeout: {str(exc)}")

        except httpx.RequestError as exc:
            logger.error(
                f"[{request_id}] Request error to {service} ({url}): {str(exc)}"
            )
            raise ServiceUnavailableError(service, f"Request failed: {str(exc)}")


async def parse_json_body(request: Request) -> Optional[dict]:
    if request.method.upper() not in BODY_METHODS:
        return None

    try:
        raw_body = await request.body()
        if not raw_body or not raw_body.strip():
            raise ValidationError(
                "body",
                "Request body is required. Provide a valid JSON object.",
            )

        return json.loads(raw_body)
    except json.JSONDecodeError as exc:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(f"[{request_id}] Invalid JSON in request body: {str(exc)}")
        raise ValidationError("body", f"Invalid JSON: {str(exc)}")


@app.get("/")
def read_root():
    return {
        "message": "API Gateway is running",
        "available_services": list(SERVICES.keys())
    }


@app.post("/auth/login", response_model=TokenResponse)
def login(credentials: LoginRequest, request: Request):
    request_id = getattr(request.state, "request_id", "unknown")

    if not credentials.username or not credentials.password:
        logger.warning(
            f"[{request_id}] Login attempt with empty credentials | Username: {bool(credentials.username)}"
        )
        raise ValidationError(
            "credentials",
            "Username and password are required",
        )

    if (
        credentials.username != AUTH_USERNAME
        or credentials.password != AUTH_PASSWORD
    ):
        logger.warning(
            f"[{request_id}] Failed login attempt | Username: {credentials.username}"
        )
        raise AuthenticationError("Invalid username or password")

    try:
        access_token = create_access_token(credentials.username)
        logger.info(
            f"[{request_id}] Successful login | User: {credentials.username}"
        )
        return TokenResponse(
            access_token=access_token,
            expires_in=JWT_EXP_MINUTES * 60,
        )
    except Exception as exc:
        logger.error(f"[{request_id}] Token generation failed: {str(exc)}")
        raise InternalServerError(f"Token generation failed: {str(exc)}")


@app.api_route(
    "/gateway/proxy/{service}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    dependencies=[Depends(get_current_user)],
)
@app.api_route(
    "/gateway/proxy/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    dependencies=[Depends(get_current_user)],
)
async def proxy_service(service: str, request: Request, path: str = ""):
    route_path = f"/{path}" if path else ""
    body = await parse_json_body(request)
    return await forward_request(
        service=service,
        path=route_path,
        method=request.method,
        json_body=body,
        params=dict(request.query_params),
        request=request,
    )


@app.get("/gateway/books", dependencies=[Depends(get_current_user)])
async def get_all_books(request: Request):
    return await forward_request(
        "books",
        "/api/books",
        "GET",
        params=dict(request.query_params),
        request=request,
    )


@app.get("/gateway/books/{book_id}", dependencies=[Depends(get_current_user)])
async def get_book(book_id: int, request: Request):
    return await forward_request("books", f"/api/books/{book_id}", "GET", request=request)


@app.post("/gateway/books", dependencies=[Depends(get_current_user)])
async def create_book(
    request: Request,
    book: Annotated[BookCreateRequest, Body(description="Book payload")],
):
    body = book.model_dump(exclude_none=True)
    return await forward_request("books", "/api/books", "POST", json_body=body, request=request)


@app.put("/gateway/books/{book_id}", dependencies=[Depends(get_current_user)])
async def update_book(
    book_id: int,
    request: Request,
    book: Annotated[
        Optional[BookUpdateRequest],
        Body(description="Fields to update for a book"),
    ] = None,
):
    if book is None:
        raise ValidationError(
            "body",
            REQUIRED_UPDATE_BODY_MESSAGE,
        )

    body = book.model_dump(exclude_unset=True, exclude_none=True)
    if not body:
        raise ValidationError(
            "body",
            EMPTY_UPDATE_BODY_MESSAGE,
        )

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
async def create_customer(
    request: Request,
    customer: Annotated[CustomerCreateRequest, Body(description="Customer payload")],
):
    body = customer.model_dump(exclude_none=True)
    return await forward_request("customers", "/api/customers", "POST", json_body=body, request=request)


@app.put("/gateway/customers/{customer_id}", dependencies=[Depends(get_current_user)])
async def update_customer(
    customer_id: int,
    request: Request,
    customer: Annotated[
        Optional[CustomerUpdateRequest],
        Body(description="Fields to update for a customer"),
    ] = None,
):
    if customer is None:
        raise ValidationError(
            "body",
            REQUIRED_UPDATE_BODY_MESSAGE,
        )

    body = customer.model_dump(exclude_unset=True, exclude_none=True)
    if not body:
        raise ValidationError(
            "body",
            EMPTY_UPDATE_BODY_MESSAGE,
        )

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
async def create_cart_item(
    request: Request,
    item: Annotated[CartItemCreateRequest, Body(description="Cart item payload")],
):
    body = item.model_dump(exclude_none=True)
    return await forward_request("cart", "/api/cart", "POST", json_body=body, request=request)


@app.put("/gateway/cart/{item_id}", dependencies=[Depends(get_current_user)])
async def update_cart_item(
    item_id: int,
    request: Request,
    item: Annotated[
        Optional[CartItemUpdate],
        Body(description="Fields to update for a cart item"),
    ] = None,
):
    if item is None:
        raise ValidationError(
            "body",
            REQUIRED_UPDATE_BODY_MESSAGE,
        )

    body = item.model_dump(exclude_unset=True, exclude_none=True)
    if not body:
        raise ValidationError(
            "body",
            EMPTY_UPDATE_BODY_MESSAGE,
        )

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
async def create_order(
    request: Request,
    order: Annotated[OrderCreateRequest, Body(description="Order payload")],
):
    body = order.model_dump(exclude_none=True)
    return await forward_request("orders", "/api/orders", "POST", json_body=body, request=request)

@app.put("/gateway/orders/{order_id}", dependencies=[Depends(get_current_user)])
async def update_order(
    order_id: str,
    request: Request,
    order: Annotated[
        Optional[OrderUpdateRequest],
        Body(description="Fields to update for an order"),
    ] = None,
):
    if order is None:
        raise ValidationError(
            "body",
            REQUIRED_UPDATE_BODY_MESSAGE,
        )

    body = order.model_dump(exclude_unset=True, exclude_none=True)
    if not body:
        raise ValidationError(
            "body",
            EMPTY_UPDATE_BODY_MESSAGE,
        )

    return await forward_request("orders", f"/api/orders/{order_id}", "PUT", json_body=body, request=request)


@app.delete("/gateway/orders/{order_id}", dependencies=[Depends(get_current_user)])
async def delete_order(order_id: str, request: Request):
    return await forward_request("orders", f"/api/orders/{order_id}", "DELETE", request=request)
