from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
from auth import require_role
from database import get_db
from models import User
from schemas import ReviewerTransactionResponse, TransactionResponse


router = APIRouter(prefix="/reviewer", tags=["fraud review"])


@router.get("/transactions", response_model=list[ReviewerTransactionResponse])
def list_suspicious_transactions(
    database: Annotated[Session, Depends(get_db)],
    reviewer: Annotated[User, Depends(require_role("REVIEWER"))],
) -> list[ReviewerTransactionResponse]:
    """Return pending cases with each customer's transaction history."""
    pending = crud.get_suspicious_transactions(database)
    return [
        ReviewerTransactionResponse.model_validate(
            {
                **TransactionResponse.model_validate(transaction).model_dump(),
                "customer_id": transaction.owner.id,
                "customer_name": transaction.owner.display_name,
                "customer_email": transaction.owner.username,
                "customer_history": crud.get_user_transactions(
                    database,
                    user_id=transaction.user_id,
                ),
            }
        )
        for transaction in pending
    ]


def _set_review_status(
    transaction_id: int,
    new_status: Literal["Reviewed", "Cleared"],
    database: Session,
) -> TransactionResponse:
    """Apply a reviewer action only to a transaction still awaiting review."""
    transaction = crud.get_transaction(database, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    if transaction.status not in ("Review", "Fraud"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transaction has already been handled",
        )
    return crud.update_transaction_status(database, transaction, new_status)


@router.put("/review/{transaction_id}", response_model=TransactionResponse)
def review_transaction(
    transaction_id: int,
    database: Annotated[Session, Depends(get_db)],
    reviewer: Annotated[User, Depends(require_role("REVIEWER"))],
) -> TransactionResponse:
    """Mark a suspicious transaction as reviewed."""
    return _set_review_status(transaction_id, "Reviewed", database)


@router.put("/clear/{transaction_id}", response_model=TransactionResponse)
def clear_transaction(
    transaction_id: int,
    database: Annotated[Session, Depends(get_db)],
    reviewer: Annotated[User, Depends(require_role("REVIEWER"))],
) -> TransactionResponse:
    """Mark a suspicious transaction as cleared by the reviewer."""
    return _set_review_status(transaction_id, "Cleared", database)
