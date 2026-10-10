import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from app.schemas.user import UserCreate
from app.services.user import register_user, authenticate_user, get_user_by_token
from app.core import security

TEST_DATABASE_URL = "sqlite:///./test_sifa.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_register_user_success(db_session):
    user_data = UserCreate(
        email="operator@sifa.com",
        full_name="Rose Muragu",
        password="SecurePassword123"
    )
    user = register_user(db_session, user_data)
    assert user.id is not None
    assert user.email == "operator@sifa.com"
    assert user.full_name == "Rose Muragu"

def test_register_user_duplicate_email_throws_exception(db_session):
    user_data = UserCreate(
        email="operator@sifa.com",
        full_name="Rose Muragu",
        password="SecurePassword123"
    )
    register_user(db_session, user_data)
    
    with pytest.raises(HTTPException) as exc_info:
        register_user(db_session, user_data)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "invalid credentials"

def test_authenticate_user_success(db_session):
    user_data = UserCreate(
        email="operator@sifa.com",
        full_name="Rose Muragu",
        password="SecurePassword123"
    )
    register_user(db_session, user_data)
    
    authenticated_user = authenticate_user(db_session, email="operator@sifa.com", password="SecurePassword123")
    assert authenticated_user.email == "operator@sifa.com"

def test_authenticate_user_invalid_credentials_throws_exception(db_session):
    user_data = UserCreate(
        email="operator@sifa.com",
        full_name="Rose Muragu",
        password="SecurePassword123"
    )
    register_user(db_session, user_data)
    
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(db_session, email="operator@sifa.com", password="WrongPassword123")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect credentials ."

def test_get_user_by_token_success(db_session):
    user_data = UserCreate(
        email="operator@sifa.com",
        full_name="Rose Muragu",
        password="SecurePassword123"
    )
    register_user(db_session, user_data)
    
    token = security.create_access_token(data={"sub": "operator@sifa.com"})
    user = get_user_by_token(db_session, token)
    assert user.email == "operator@sifa.com"

def test_get_user_by_token_invalid_or_expired_throws_exception(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_user_by_token(db_session, token="invalid_or_expired_jwt_signature")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"
