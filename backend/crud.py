from sqlalchemy.orm import Session

from engine import FraudAssessment
from models import Transaction
from schemas import TransactionCreate


def get_previous_transaction(
    database: Session,
    user_id: int,
    account_id: str,
) -> Transaction | None:
    """Find the most recent transaction for this customer's account."""
    return (
        database.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.account_id == account_id,
        )
        .order_by(Transaction.created_at.desc(), Transaction.id.desc())
        .first()
    )


def create_transaction(
    database: Session,
    user_id: int,
    transaction_data: TransactionCreate,
    assessment: FraudAssessment,
) -> Transaction:
    """Persist a submitted transaction together with its fraud assessment."""
    transaction = Transaction(
        user_id=user_id,
        account_id=transaction_data.account_id,
        amount=transaction_data.amount,
        country=transaction_data.country,
        device="",
        risk_score=assessment.risk_score,
        status=assessment.status,
        reasons=assessment.reasons,
    )
    database.add(transaction)
    database.commit()
    database.refresh(transaction)
    return transaction


def get_user_transactions(database: Session, user_id: int) -> list[Transaction]:
    """Return only the transactions owned by the requested customer."""
    return (
        database.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc(), Transaction.id.desc())
        .all()
    )


def get_suspicious_transactions(database: Session) -> list[Transaction]:
    """Return pending cases highest-risk first, with older ties ahead."""
    return (
        database.query(Transaction)
        .filter(Transaction.status.in_(("Review", "Fraud")))
        .order_by(
            Transaction.risk_score.desc(),
            Transaction.created_at.asc(),
            Transaction.id.asc(),
        )
        .all()
    )


def get_transaction(database: Session, transaction_id: int) -> Transaction | None:
    """Find one transaction by its primary key."""
    return database.query(Transaction).filter(Transaction.id == transaction_id).first()


def update_transaction_status(
    database: Session,
    transaction: Transaction,
    new_status: str,
) -> Transaction:
    """Save a reviewer's decision for an existing transaction."""
    transaction.status = new_status
    database.commit()
    database.refresh(transaction)
    return transaction
