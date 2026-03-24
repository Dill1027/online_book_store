from datetime import datetime, timezone

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BookBase(BaseModel):
    bookId: str = Field(pattern=r"^B\d{3}$")
    title: str = Field(min_length=1)
    price: float = Field(ge=0)
    quantity: int = Field(ge=0)
    status: str = "Active"


class BookCreate(BookBase):
    pass


class Book(BookBase):
    createdAt: datetime = Field(default_factory=utcnow)
    updatedAt: datetime = Field(default_factory=utcnow)
