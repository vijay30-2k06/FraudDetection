from dataclasses import dataclass
from typing import Literal

from models import Transaction
from schemas import TransactionCreate
from rules.amount_rule import AmountRule
from rules.base_rule import FraudRule
from rules.country_rule import CountryRule


@dataclass(frozen=True)
class FraudAssessment:
    risk_score: int
    status: Literal["Safe", "Review", "Fraud"]
    reasons: list[str]


class FraudEngine:
    """Run configured strategies and combine their independent assessments."""

    def __init__(self, rules: list[FraudRule] | None = None) -> None:
        self.rules = tuple(
            rules
            if rules is not None
            else (AmountRule(), CountryRule())
        )

    def evaluate(
        self,
        transaction: TransactionCreate,
        previous_transaction: Transaction | None = None,
    ) -> FraudAssessment:
        score = 0
        reasons: list[str] = []

        for rule in self.rules:
            result = rule.evaluate(transaction, previous_transaction)
            score += result.score
            if result.reason:
                reasons.append(result.reason)

        score = min(score, 100)
        if score >= 70:
            status: Literal["Safe", "Review", "Fraud"] = "Fraud"
        elif score >= 40:
            status = "Review"
        else:
            status = "Safe"

        return FraudAssessment(risk_score=score, status=status, reasons=reasons)
