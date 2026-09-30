from models import Transaction
from schemas import TransactionCreate

from rules.base_rule import FraudRule, RuleResult


class AmountRule(FraudRule):
    """Flag transactions whose amount exceeds the configured threshold."""

    def evaluate(
        self,
        transaction: TransactionCreate,
        previous_transaction: Transaction | None,
    ) -> RuleResult:
        if transaction.amount > 50000:
            return RuleResult(score=40, reason="High Transaction Amount")
        return RuleResult()
