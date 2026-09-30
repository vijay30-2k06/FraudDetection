from models import Transaction
from schemas import TransactionCreate

from rules.base_rule import FraudRule, RuleResult


class CountryRule(FraudRule):
    """Flag an account's first transaction from a different country."""

    def evaluate(
        self,
        transaction: TransactionCreate,
        previous_transaction: Transaction | None,
    ) -> RuleResult:
        if previous_transaction is None:
            return RuleResult()

        previous_country = previous_transaction.country.strip().casefold()
        current_country = transaction.country.strip().casefold()
        if previous_country != current_country:
            return RuleResult(score=30, reason="Transaction from New Country")
        return RuleResult()
