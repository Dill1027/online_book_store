from typing import List
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import Customer, CustomerCreate, CustomerUpdate
from service import CustomerService

app = FastAPI(title="Customer Service", version="1.0.0")
customer_service = CustomerService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with custom error message"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:])
        message = error["msg"]
        errors.append({"field": field, "message": message})
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation failed",
            "errors": errors
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value validation errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Invalid request data",
            "error": str(exc)
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error_type": type(exc).__name__,
            "error": str(exc)
        },
    )


@app.get("/")
def read_root():
    return {"message": "Customer Service is running"}


@app.get("/api/customers", response_model=List[Customer])
def get_all_customers():
    return customer_service.get_all()


@app.get("/api/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: int):
    customer = customer_service.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/api/customers", response_model=Customer, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate):
    created_customer = customer_service.create(customer)
    if not created_customer:
        raise HTTPException(status_code=400, detail="Email already exists")
    return created_customer


@app.put("/api/customers/{customer_id}", response_model=Customer)
def update_customer(customer_id: int, customer: CustomerUpdate):
    updated_customer = customer_service.update(customer_id, customer)
    if not updated_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated_customer


@app.delete("/api/customers/{customer_id}")
def delete_customer(customer_id: int):
    success = customer_service.delete(customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}
