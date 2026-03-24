from datetime import datetime, timezone

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CartItemBase(BaseModel):
    cartId: str = Field(pattern=r"^CRT\d{3}$")
    customerId: str = Field(pattern=r"^C\d{3}$")
    bookId: str = Field(pattern=r"^B\d{3}$")
    title: str = Field(min_length=1)
    price: float = Field(ge=0)
    quantity: int = Field(ge=1)
    status: str = "Pending"


class CartItemCreate(CartItemBase):
    pass


class CartItem(CartItemBase):
    createdAt: datetime = Field(default_factory=utcnow)
    updatedAt: datetime = Field(default_factory=utcnow)
