import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

if not SECRET_KEY:
    raise RuntimeError(
        "CRITICAL ERROR: SECRET_KEY is missing from the environment variables (.env)."
    )

def hash_password(password: str) -> str:
    if not password or not password.strip():
        raise ValueError("Password cannot be empty.")
    salt = secrets.token_bytes(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return f"{salt.hex()}:{hash_bytes.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        salt_hex, original_hash_hex = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)
        new_hash = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode("utf-8"), salt, 100000
        )
        return secrets.compare_digest(new_hash.hex(), original_hash_hex)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    if not data or "sub" not in data:
        raise ValueError("Token data must contain a 'sub' claim identifier.")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update(
        {"exp": expire, "iat": datetime.now(timezone.utc).timestamp(), "type": "access"}
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    if not token or not token.strip():
        raise ValueError("Token missing")
    try:
        payload: dict[str, any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str = payload.get("sub")
        if not sub or not str(sub).strip():
            raise ValueError("Token is missing user identifier (sub claim)")
        token_type = payload.get("type")
        if token_type and token_type != "access":
            raise ValueError("Invalid token scope")
        iat = payload.get("iat")
        if iat and datetime.now(timezone.utc).timestamp() < iat:
            raise ValueError("Token issued in the future")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token signature or payload")
