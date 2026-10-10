import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core import security
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate

def register_user(db: Session, user_data: UserCreate):
    existing_user = UserRepository(db).get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid credentials"
        )
    hashed_password = security.hash_password(user_data.password)
    return UserRepository(db).create_user(user_data)




def authenticate_user(db: Session, email: str, password: str):
    user = UserRepository(db).get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials .",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not security.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials .",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_user_by_token(db: Session, token: str):
    try:
        payload = security.decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = UserRepository(db).get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
