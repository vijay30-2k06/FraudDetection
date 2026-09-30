import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from models import Transaction


logger = logging.getLogger(__name__)


def send_fraud_alert(transaction: Transaction) -> bool:
    """Send a fraud alert through SES when AWS email settings are available."""
    region = os.getenv("AWS_REGION", "us-east-1")
    sender = os.getenv("SES_FROM_EMAIL")
    reviewer = os.getenv("SES_REVIEWER_EMAIL")
    if not sender or not reviewer:
        logger.info("SES alert skipped because sender or reviewer email is unset")
        return False

    reasons = "\n".join(f"- {reason}" for reason in transaction.reasons) or "- No rule reasons"
    body = (
        f"Transaction ID: {transaction.id}\n"
        f"Account ID: {transaction.account_id}\n"
        f"Amount: {transaction.amount}\n"
        f"Risk Score: {transaction.risk_score}\n"
        f"Reasons:\n{reasons}"
    )

    try:
        client = boto3.client("ses", region_name=region)
        client.send_email(
            Source=sender,
            Destination={"ToAddresses": [reviewer]},
            Message={
                "Subject": {"Data": "Fraud Alert", "Charset": "UTF-8"},
                "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
            },
        )
    except (BotoCoreError, ClientError):
        logger.exception("SES failed to send alert for transaction %s", transaction.id)
        return False

    return True
