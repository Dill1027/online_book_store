from pydantic import BaseModel, field_validator
from typing import Optional
import re


def _validate_phone_number(value: str) -> str:
    cleaned = value.strip()
    if not cleaned.isdigit():
        raise ValueError("Phone number must contain only digits")

    is_country_format = cleaned.startswith("94") and len(cleaned) == 11
    is_local_format = cleaned.startswith("0") and len(cleaned) == 10

    if not (is_country_format or is_local_format):
        raise ValueError("Phone number must be 94 + 9 digits or 0 + 9 digits")

    return cleaned


def _validate_email_address(value: str) -> str:
    cleaned = value.strip().lower()
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, cleaned):
        raise ValueError("Invalid email address format")
    return cleaned


class Customer(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    address: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "String",
                "email": "string@example.com",
                "phone": "94########",
                "address": "string",
            }
        }


class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: str
    address: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return _validate_phone_number(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return _validate_email_address(value)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "String",
                "email": "string@example.com",
                "phone": "94########",
                "address": "string",
            }
        }


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _validate_phone_number(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _validate_email_address(value)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "String",
                "email": "string@example.com",
                "phone": "94########",
                "address": "string",
            }
        }
