from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import crud
from auth import require_role
from database import get_db
from engine import FraudEngine
from models import User
from notification import send_fraud_alert
from schemas import CustomerTransactionResponse, TransactionCreate


router = APIRouter(tags=["customer transactions"])


@router.post(
    "/transaction",
    response_model=CustomerTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_transaction(
    transaction_data: TransactionCreate,
    database: Annotated[Session, Depends(get_db)],
    customer: Annotated[User, Depends(require_role("CUSTOMER"))],
) -> CustomerTransactionResponse:
    """Assess and store a customer transaction without exposing its score."""
    previous = crud.get_previous_transaction(
        database,
        user_id=customer.id,
        account_id=transaction_data.account_id,
    )
    assessment = FraudEngine().evaluate(transaction_data, previous)
    transaction = crud.create_transaction(
        database,
        user_id=customer.id,
        transaction_data=transaction_data,
        assessment=assessment,
    )
    if transaction.risk_score >= 70:
        send_fraud_alert(transaction)
    return transaction


@router.get("/my-transactions", response_model=list[CustomerTransactionResponse])
def list_my_transactions(
    database: Annotated[Session, Depends(get_db)],
    customer: Annotated[User, Depends(require_role("CUSTOMER"))],
) -> list[CustomerTransactionResponse]:
    """Return only transactions belonging to the signed-in customer."""
    return crud.get_user_transactions(database, user_id=customer.id)
