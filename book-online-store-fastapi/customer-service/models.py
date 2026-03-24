from datetime import datetime, timezone

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CustomerBase(BaseModel):
    customerId: str = Field(pattern=r"^C\d{3}$")
    title: str = "Customer"
    status: str = "Active"


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    createdAt: datetime = Field(default_factory=utcnow)
    updatedAt: datetime = Field(default_factory=utcnow)
