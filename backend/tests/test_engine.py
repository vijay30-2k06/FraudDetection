from decimal import Decimal

from engine import FraudEngine
from models import Transaction
from schemas import TransactionCreate


def make_transaction(
    amount: str = "100.00",
    country: str = "US",
) -> TransactionCreate:
    """Build a valid input transaction for focused rule tests."""
    return TransactionCreate(
        account_id="account-1",
        amount=Decimal(amount),
        country=country,
    )


def test_amount_rule_uses_strict_greater_than_threshold() -> None:
    engine = FraudEngine()

    at_threshold = engine.evaluate(make_transaction("50000.00"))
    above_threshold = engine.evaluate(make_transaction("50000.01"))

    assert (at_threshold.risk_score, at_threshold.status) == (0, "Safe")
    assert (above_threshold.risk_score, above_threshold.status) == (40, "Review")
    assert above_threshold.reasons == ["High Transaction Amount"]


def test_country_rule_adds_review_points() -> None:
    previous = Transaction(country="US")

    assessment = FraudEngine().evaluate(
        make_transaction(country="CA"),
        previous,
    )

    assert assessment.risk_score == 30
    assert assessment.status == "Safe"
    assert assessment.reasons == ["Transaction from New Country"]


def test_amount_and_country_rules_classify_as_fraud() -> None:
    previous = Transaction(country="US")

    assessment = FraudEngine().evaluate(
        make_transaction("50000.01", "CA"),
        previous,
    )

    assert assessment.risk_score == 70
    assert assessment.status == "Fraud"
    assert len(assessment.reasons) == 2


def test_country_comparison_is_case_insensitive() -> None:
    previous = Transaction(country="US")

    assessment = FraudEngine().evaluate(
        make_transaction(country="us"),
        previous,
    )

    assert assessment.risk_score == 0
