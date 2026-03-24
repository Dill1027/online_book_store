from fastapi import FastAPI, HTTPException, status

from data_service import CustomerDataService
from models import Customer, CustomerCreate
from service import CustomerService

app = FastAPI(title="customer-service")

customer_service = CustomerService(CustomerDataService())


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "customer-service", "status": "ok"}


@app.get("/customers")
def list_customers() -> list[Customer]:
    return customer_service.list_customers()


@app.get("/customers/{customer_id}")
def get_customer_by_customer_id(customer_id: str) -> Customer:
    customer = customer_service.get_customer_by_customer_id(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@app.post("/customers", status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate) -> Customer:
    try:
        return customer_service.create_customer(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
