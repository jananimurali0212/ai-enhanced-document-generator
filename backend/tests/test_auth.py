"""
Unit & Integration Tests for Authentication (Module 2).
Verifies missing, invalid, expired, and valid tokens.
"""

import sys
import time
import uuid
from pathlib import Path
import jwt
import pytest
from fastapi import HTTPException

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.auth import get_current_user, _verify_jwt_token, AuthenticatedUser
from app.core.config import settings

def test_missing_authorization_header():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(authorization=None)
    assert exc_info.value.status_code == 401
    assert "Missing Authorization header" in exc_info.value.detail

def test_invalid_authorization_format():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(authorization="Basic dXNlcjpwYXNz")
    assert exc_info.value.status_code == 401
    assert "Invalid Authorization format" in exc_info.value.detail

def test_empty_bearer_token():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(authorization="Bearer   ")
    assert exc_info.value.status_code == 401

def test_expired_token():
    secret = "test-secret-key-for-jwt-testing-12345"
    expired_payload = {
        "sub": str(uuid.uuid4()),
        "exp": time.time() - 3600,  # 1 hour in the past
        "aud": "authenticated"
    }
    expired_token = jwt.encode(expired_payload, secret, algorithm="HS256")
    
    # Test with configured secret
    old_secret = settings.SUPABASE_JWT_SECRET
    settings.SUPABASE_JWT_SECRET = secret
    try:
        with pytest.raises(HTTPException) as exc_info:
            _verify_jwt_token(expired_token)
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()
    finally:
        settings.SUPABASE_JWT_SECRET = old_secret

def test_invalid_signature_token():
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.payload"
    old_allow = settings.ALLOW_DEMO_AUTH
    settings.ALLOW_DEMO_AUTH = False
    try:
        with pytest.raises(HTTPException) as exc_info:
            _verify_jwt_token(invalid_token)
        assert exc_info.value.status_code == 401
    finally:
        settings.ALLOW_DEMO_AUTH = old_allow

def test_valid_authenticated_user_token():
    secret = "valid-test-secret-supabase-12345678"
    user_uuid = str(uuid.uuid4())
    valid_payload = {
        "sub": user_uuid,
        "email": "engineer@enterprise.com",
        "role": "authenticated",
        "aud": "authenticated",
        "exp": time.time() + 3600
    }
    token = jwt.encode(valid_payload, secret, algorithm="HS256")

    old_secret = settings.SUPABASE_JWT_SECRET
    settings.SUPABASE_JWT_SECRET = secret
    try:
        user = get_current_user(authorization=f"Bearer {token}")
        assert isinstance(user, AuthenticatedUser)
        assert user.id == user_uuid
        assert user.email == "engineer@enterprise.com"
        assert user.role == "authenticated"
    finally:
        settings.SUPABASE_JWT_SECRET = old_secret

def test_demo_token_parsing():
    demo_uid = str(uuid.uuid4())
    user = get_current_user(authorization=f"Bearer mock-user-{demo_uid}")
    assert user.id == demo_uid
    assert user.email == f"{demo_uid}@example.com"
