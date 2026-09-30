from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """A login account with either customer or reviewer permissions."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False, default="")
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)

    transactions = relationship(
        "Transaction",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Transaction(Base):
    """A submitted transaction and its fraud assessment results."""

    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="check_transaction_amount_positive"),
        CheckConstraint(
            "risk_score >= 0 AND risk_score <= 100",
            name="check_transaction_risk_score_range",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_id = Column(String(100), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    country = Column(String(100), nullable=False)
    device = Column(String(255), nullable=False)
    risk_score = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="Safe", index=True)
    reasons = Column(JSON, nullable=False, default=list)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    owner = relationship("User", back_populates="transactions")
