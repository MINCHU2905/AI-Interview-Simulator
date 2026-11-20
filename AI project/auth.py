"""Authentication helpers backed by bcrypt and SQLite."""
from __future__ import annotations

import bcrypt

from database import create_user, get_user_by_email


def validate_registration(name: str, email: str, password: str, confirmation: str) -> str | None:
    if len(name.strip()) < 2:
        return "Please enter your full name."
    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        return "Enter a valid email address."
    if len(password) < 8:
        return "Use a password of at least 8 characters."
    if password != confirmation:
        return "Passwords do not match."
    if get_user_by_email(email):
        return "An account with this email already exists."
    return None


def register_user(name: str, email: str, password: str) -> int:
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return create_user(name, email, password_hash)


def authenticate_user(email: str, password: str) -> dict | None:
    user = get_user_by_email(email)
    if not user:
        return None
    stored_hash = user["password_hash"]
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")
    return user if bcrypt.checkpw(password.encode("utf-8"), stored_hash) else None
