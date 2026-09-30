import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from auth import hash_password
from database import Base, SessionLocal, engine
from models import User
from routes.auth import router as auth_router
from routes.review import router as review_router
from routes.transaction import router as transaction_router


def ensure_user_display_name_column(database_engine: Engine = engine) -> None:
    """Add the display-name column to an existing SQLite users table if needed."""
    if not inspect(database_engine).has_table("users"):
        return

    columns = {column["name"] for column in inspect(database_engine).get_columns("users")}
    if "display_name" not in columns:
        with database_engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE users ADD COLUMN display_name "
                    "VARCHAR(100) NOT NULL DEFAULT ''"
                )
            )


def seed_demo_users(database: Session) -> None:
    """Create the configured email accounts and migrate legacy demo identities."""
    demo_users = (
        ("customer", "vijay.k.302006@gmail.com", "123456", "CUSTOMER", "Vijay K"),
        ("reviewer", "john@gmail.com", "qwerty", "REVIEWER", "John"),
        (None, "ben@gmail.com", "789456", "CUSTOMER", "Ben"),
        (None, "kevin@gmail.com", "123789", "CUSTOMER", "Kevin"),
    )
    for legacy_username, email, password, role, display_name in demo_users:
        user = database.query(User).filter(User.username == email).first()
        legacy_user = None
        if legacy_username:
            legacy_user = (
                database.query(User)
                .filter(User.username == legacy_username)
                .first()
            )

        if user is None and legacy_user is not None:
            user = legacy_user
            user.username = email
        elif user is None:
            user = User(
                username=email,
                display_name=display_name,
                role=role,
                hashed_password="",
            )
            database.add(user)
        elif legacy_user is not None and legacy_user.id != user.id:
            for transaction in legacy_user.transactions:
                transaction.user_id = user.id
            database.delete(legacy_user)

        user.role = role
        user.display_name = display_name
        user.hashed_password = hash_password(password)
    database.commit()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create tables and seed local demo users before serving requests."""
    Base.metadata.create_all(bind=engine)
    ensure_user_display_name_column()
    with SessionLocal() as database:
        seed_demo_users(database)
    yield


app = FastAPI(
    title="Fraud Detection Rule Engine",
    description="Rule-based transaction assessment and reviewer workflow.",
    version="1.0.0",
    lifespan=lifespan,
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(transaction_router)
app.include_router(review_router)


@app.get("/", tags=["health"])
def health_check() -> dict[str, str]:
    """Provide a small health response for local checks and deployment probes."""
    return {"status": "ok"}
