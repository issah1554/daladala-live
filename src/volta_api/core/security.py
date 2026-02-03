import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from enum import Enum

from jose import jwt, JWTError
from passlib.context import CryptContext


# Configuration - move these to env later
SECRET_KEY = "dev-secret-change-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 30
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS = 24


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

_revoked_access_tokens: dict[str, float] = {}


# ===== Password Hashing =====


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ===== Token Creation =====


def create_access_token(subject: str) -> str:
    """Create an access token for authentication."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "exp": expire,
        "type": TokenType.ACCESS.value,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Create a refresh token for obtaining new access tokens."""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": subject,
        "exp": expire,
        "type": TokenType.REFRESH.value,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_password_reset_token(subject: str) -> str:
    """Create a token for password reset."""
    expire = datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "exp": expire,
        "type": TokenType.PASSWORD_RESET.value,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_email_verification_token(subject: str) -> str:
    """Create a token for email verification."""
    expire = datetime.utcnow() + timedelta(hours=EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": subject,
        "exp": expire,
        "type": TokenType.EMAIL_VERIFICATION.value,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ===== Token Verification =====


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token. Returns payload or None if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, expected_type: TokenType) -> Optional[str]:
    """
    Verify a token and check its type.
    Returns the subject (user ID) if valid, None otherwise.
    """
    payload = decode_token(token)
    if not payload:
        return None

    token_type = payload.get("type")
    if token_type != expected_type.value:
        return None

    subject = payload.get("sub")
    return subject


def verify_access_token(token: str) -> Optional[str]:
    """Verify an access token. Returns user_id if valid."""
    if is_access_token_revoked(token):
        return None
    return verify_token(token, TokenType.ACCESS)


def verify_refresh_token(token: str) -> Optional[str]:
    """Verify a refresh token. Returns user_id if valid."""
    return verify_token(token, TokenType.REFRESH)


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify a password reset token. Returns user_id if valid."""
    return verify_token(token, TokenType.PASSWORD_RESET)


def verify_email_verification_token(token: str) -> Optional[str]:
    """Verify an email verification token. Returns user_id if valid."""
    return verify_token(token, TokenType.EMAIL_VERIFICATION)


# ===== Utility Functions =====


def generate_random_token(length: int = 32) -> str:
    """Generate a random URL-safe token."""
    return secrets.token_urlsafe(length)


def revoke_access_token(token: str) -> bool:
    payload = decode_token(token)
    if not payload or payload.get("type") != TokenType.ACCESS.value:
        return False

    exp = payload.get("exp")
    if exp is None:
        return False

    _revoked_access_tokens[token] = float(exp)
    return True


def is_access_token_revoked(token: str) -> bool:
    _cleanup_revoked_tokens()
    return token in _revoked_access_tokens


def _cleanup_revoked_tokens() -> None:
    now_ts = datetime.now(timezone.utc).timestamp()
    expired = [tok for tok, exp in _revoked_access_tokens.items() if exp <= now_ts]
    for tok in expired:
        _revoked_access_tokens.pop(tok, None)
