from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    email: EmailStr = Field(validation_alias="username")
    display_name: str
    role: Literal["CUSTOMER", "REVIEWER"]

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TransactionCreate(BaseModel):
    account_id: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    country: str = Field(min_length=2, max_length=100)


class CustomerTransactionResponse(BaseModel):
    id: int
    account_id: str
    amount: Decimal
    country: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionResponse(BaseModel):
    id: int
    account_id: str
    amount: Decimal
    country: str
    risk_score: int = Field(ge=0, le=100)
    status: Literal["Safe", "Review", "Fraud", "Reviewed", "Cleared"]
    reasons: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewerTransactionResponse(TransactionResponse):
    customer_id: int
    customer_name: str
    customer_email: EmailStr
    customer_history: list[TransactionResponse]