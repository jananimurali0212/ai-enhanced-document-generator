"""
Authentication & Identity Verification module for FastAPI.
Extracts and cryptographically verifies Supabase JWT access tokens,
deriving authenticated user identity without trusting client-supplied user IDs.
"""

import time
import logging
import uuid
from typing import Optional
from dataclasses import dataclass
import jwt
from fastapi import Header, HTTPException, status, Depends
from app.core.config import settings
from app.services.supabase_service import supabase_service

logger = logging.getLogger(__name__)

@dataclass
class AuthenticatedUser:
    id: str
    email: Optional[str] = None
    role: str = "authenticated"
    token: str = ""

def _verify_jwt_token(token: str) -> dict:
    """Verifies JWT using SUPABASE_JWT_SECRET or Supabase Auth API."""
    # 1. Check if token is a demo/test token when DEMO_AUTH is permitted
    if settings.ALLOW_DEMO_AUTH:
        if token.startswith("demo-token-") or token.startswith("mock-user-"):
            user_id = token.replace("demo-token-", "").replace("mock-user-", "")
            # Ensure valid UUID format for user_id
            try:
                valid_uuid = str(uuid.UUID(user_id))
            except ValueError:
                # Deterministic UUID for demo users
                valid_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))
            return {
                "sub": valid_uuid,
                "email": f"{user_id}@example.com",
                "role": "authenticated",
                "aud": "authenticated"
            }

    # 2. Local verification using SUPABASE_JWT_SECRET if configured
    if settings.SUPABASE_JWT_SECRET:
        try:
            # Supabase tokens use HS256 by default with the project JWT secret
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256", "RS256"],
                options={"verify_aud": False}  # Supabase aud is 'authenticated'
            )
            # Verify audience
            aud = payload.get("aud")
            if aud and aud != "authenticated":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token audience. Expected 'authenticated'."
                )
            # Verify expiration
            exp = payload.get("exp")
            if exp and exp < time.time():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired."
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token signature has expired. Please sign in again."
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT signature verification failed: {e}")
            # Fall through to Supabase API check if secret check fails

    # 3. Supabase Auth API verification if client is configured
    if supabase_service.is_available:
        try:
            client = supabase_service.get_anon_client()
            if client:
                user_res = client.auth.get_user(token)
                if user_res and user_res.user:
                    return {
                        "sub": user_res.user.id,
                        "email": user_res.user.email,
                        "role": user_res.user.role or "authenticated"
                    }
        except Exception as e:
            logger.error(f"Supabase Auth token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed with authentication provider: {str(e)}"
            )

    # 4. Fallback for unconfigured dev environment
    if not settings.is_supabase_configured and settings.ALLOW_DEMO_AUTH:
        # Development fallback: decode unverified payload to extract sub if valid JWT structure
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            if "sub" in unverified:
                return unverified
        except Exception:
            pass
        # Deterministic default demo user for local frontend testing
        return {
            "sub": "a0000000-0000-0000-0000-000000000001",
            "email": "demo.user@example.com",
            "role": "authenticated"
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or unverified authentication token."
    )

def get_current_user(authorization: Optional[str] = Header(None)) -> AuthenticatedUser:
    """
    FastAPI dependency that enforces authentication.
    Extracts and validates the Bearer token from the Authorization header.
    Returns the verified AuthenticatedUser with their immutable user ID.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization format. Expected 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = parts[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty Bearer token provided.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    payload = _verify_jwt_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing user subject ('sub').",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return AuthenticatedUser(
        id=str(user_id),
        email=payload.get("email"),
        role=payload.get("role", "authenticated"),
        token=token
    )

def get_optional_current_user(authorization: Optional[str] = Header(None)) -> Optional[AuthenticatedUser]:
    """Optional authentication dependency for endpoints that support both guest and logged-in users."""
    if not authorization:
        return None
    try:
        return get_current_user(authorization)
    except HTTPException:
        return None
