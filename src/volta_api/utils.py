# src/volta_api/utils.py
import secrets
import base64


def generate_base64_id(length: int = 11) -> str:
    """Generate a URL-safe base64 public ID with the given length (default 11)."""
    random_bytes = secrets.token_bytes(8)  # 64 bits
    b64 = base64.urlsafe_b64encode(random_bytes).decode("utf-8")
    return b64.rstrip("=")[:length]
