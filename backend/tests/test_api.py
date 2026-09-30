import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from auth import hash_password
from database import Base, get_db
from models import User
from app import seed_demo_users
from routes.auth import router as auth_router
from routes.review import router as review_router
from routes.transaction import router as transaction_router


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Provide an isolated in-memory API and preloaded test accounts."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    test_sessions = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    test_app = FastAPI()
    test_app.include_router(auth_router)
    test_app.include_router(transaction_router)
    test_app.include_router(review_router)

    def override_get_db():
        database = test_sessions()
        try:
            yield database
        finally:
            database.close()

    test_app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr("routes.transaction.send_fraud_alert", lambda _: False)

    with test_sessions() as database:
        database.add_all(
            [
                User(
                    username="customer@example.com",
                    display_name="Customer One",
                    hashed_password=hash_password("1234"),
                    role="CUSTOMER",
                ),
                User(
                    username="customer2@example.com",
                    display_name="Customer Two",
                    hashed_password=hash_password("1234"),
                    role="CUSTOMER",
                ),
                User(
                    username="reviewer@example.com",
                    display_name="Reviewer One",
                    hashed_password=hash_password("1234"),
                    role="REVIEWER",
                ),
            ]
        )
        database.commit()

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()
    test_engine.dispose()


def login(client: TestClient, username: str) -> dict[str, str]:
    """Authenticate a fixture account and return its bearer header."""
    response = client.post("/login", json={"email": username, "password": "1234"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_invalid_login_returns_401(client: TestClient) -> None:
    response = client.post("/login", json={"email": "customer@example.com", "password": "wrong"})

    assert response.status_code == 401


def test_customer_scope_and_reviewer_workflow(client: TestClient) -> None:
    customer_headers = login(client, "customer@example.com")
    reviewer_headers = login(client, "reviewer@example.com")

    initial = client.post(
        "/transaction",
        headers=customer_headers,
        json={"account_id": "account-1", "amount": "100", "country": "US"},
    )
    assert initial.status_code == 201
    assert "risk_score" not in initial.json()
    assert "status" not in initial.json()

    flagged = client.post(
        "/transaction",
        headers=customer_headers,
        json={"account_id": "account-1", "amount": "50001", "country": "CA"},
    )
    assert flagged.status_code == 201
    assert "risk_score" not in flagged.json()
    assert "status" not in flagged.json()

    review_case = client.post(
        "/transaction",
        headers=customer_headers,
        json={"account_id": "account-2", "amount": "50000.01", "country": "US"},
    )
    assert review_case.status_code == 201

    my_transactions = client.get("/my-transactions", headers=customer_headers)
    assert my_transactions.status_code == 200
    assert len(my_transactions.json()) == 3
    assert all("risk_score" not in item and "status" not in item for item in my_transactions.json())

    pending = client.get("/reviewer/transactions", headers=reviewer_headers)
    assert [item["account_id"] for item in pending.json()] == ["account-1", "account-2"]
    assert pending.json()[0]["risk_score"] == 70
    assert pending.json()[0]["customer_name"] == "Customer One"
    assert pending.json()[0]["customer_email"] == "customer@example.com"
    assert [item["status"] for item in pending.json()[0]["customer_history"]] == ["Review", "Fraud", "Safe"]
    flagged_id = pending.json()[0]["id"]

    reviewed = client.put(
        f"/reviewer/review/{flagged_id}",
        headers=reviewer_headers,
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "Reviewed"
    remaining_queue = client.get("/reviewer/transactions", headers=reviewer_headers).json()
    assert [item["account_id"] for item in remaining_queue] == ["account-2"]

    assert client.put(
        f"/reviewer/clear/{initial.json()['id']}",
        headers=reviewer_headers,
    ).status_code == 409
    assert client.put("/reviewer/clear/999", headers=reviewer_headers).status_code == 404


def test_roles_and_customer_ownership_are_enforced(client: TestClient) -> None:
    customer_headers = login(client, "customer@example.com")
    second_customer_headers = login(client, "customer2@example.com")
    reviewer_headers = login(client, "reviewer@example.com")

    assert client.get("/reviewer/transactions", headers=customer_headers).status_code == 403
    assert client.post(
        "/transaction",
        headers=reviewer_headers,
        json={"account_id": "account-1", "amount": "100", "country": "US"},
    ).status_code == 403

    submitted = client.post(
        "/transaction",
        headers=second_customer_headers,
        json={"account_id": "account-1", "amount": "100", "country": "JP"},
    )
    assert submitted.status_code == 201
    assert "risk_score" not in submitted.json()
    assert client.get("/my-transactions", headers=customer_headers).json() == []
    assert len(client.get("/my-transactions", headers=second_customer_headers).json()) == 1

    reviewer_queue = client.get("/reviewer/transactions", headers=reviewer_headers)
    assert reviewer_queue.status_code == 200
    assert reviewer_queue.json() == []


def test_seed_demo_users_migrates_legacy_accounts_and_preserves_history() -> None:
    test_engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=test_engine)
    test_sessions = sessionmaker(bind=test_engine)

    with test_sessions() as database:
        legacy_customer = User(
            username="customer",
            hashed_password=hash_password("1234"),
            role="CUSTOMER",
        )
        database.add(legacy_customer)
        database.commit()
        original_id = legacy_customer.id

        seed_demo_users(database)

        migrated = database.query(User).filter_by(username="vijay.k.302006@gmail.com").one()
        reviewer = database.query(User).filter_by(username="john@gmail.com").one()
        ben = database.query(User).filter_by(username="ben@gmail.com").one()
        kevin = database.query(User).filter_by(username="kevin@gmail.com").one()
        assert migrated.id == original_id
        assert migrated.role == "CUSTOMER"
        assert migrated.display_name == "Vijay K"
        assert reviewer.role == "REVIEWER"
        assert reviewer.display_name == "John"
        assert ben.display_name == "Ben"
        assert kevin.display_name == "Kevin"
        assert client_password_check(migrated.hashed_password, "123456")
        assert client_password_check(reviewer.hashed_password, "qwerty")
        assert client_password_check(ben.hashed_password, "789456")
        assert client_password_check(kevin.hashed_password, "123789")

    test_engine.dispose()


def client_password_check(stored_hash: str, password: str) -> bool:
    """Verify the seeded login credential in the seed migration test."""
    from auth import verify_password

    return verify_password(password, stored_hash)