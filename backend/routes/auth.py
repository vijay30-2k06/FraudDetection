from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import create_access_token, verify_password
from database import get_db
from models import User
from schemas import LoginRequest, TokenResponse


router = APIRouter(tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, database: Session = Depends(get_db)) -> TokenResponse:
    """Validate credentials and return a signed bearer token."""
    user = database.query(User).filter(User.username == credentials.email).first()
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token, user=user)
