import hashlib
import os
import secrets
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database import get_db
from models import User


SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def _password_material(password: str) -> bytes:
    """Pre-hash passwords so bcrypt can safely accept inputs over 72 bytes."""
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    """Return a salted bcrypt hash suitable for storing in the users table."""
    password_hash = bcrypt.hashpw(_password_material(password), bcrypt.gensalt())
    return password_hash.decode("utf-8")


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Check a submitted password against its stored bcrypt hash."""
    return bcrypt.checkpw(
        _password_material(plain_password),
        stored_hash.encode("utf-8"),
    )


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Encode token claims with an expiration time and the configured secret."""
    token_data = data.copy()
    expiration = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    token_data["exp"] = expiration
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    database: Annotated[Session, Depends(get_db)],
) -> User:
    """Decode a bearer token and load its active user from the database."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError as error:
        raise unauthorized from error

    if not isinstance(username, str):
        raise unauthorized

    user = database.query(User).filter(User.username == username).first()
    if user is None:
        raise unauthorized
    return user


def require_role(required_role: str) -> Callable[..., User]:
    """Return a FastAPI dependency that permits only the requested role."""

    def role_dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return role_dependency