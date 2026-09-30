from abc import ABC, abstractmethod
from dataclasses import dataclass

from models import Transaction
from schemas import TransactionCreate


@dataclass(frozen=True)
class RuleResult:
    score: int = 0
    reason: str | None = None


class FraudRule(ABC):
    """Common strategy interface implemented by every fraud rule."""

    @abstractmethod
    def evaluate(
        self,
        transaction: TransactionCreate,
        previous_transaction: Transaction | None,
    ) -> RuleResult:
        """Return the risk points and optional reason produced by this rule."""
