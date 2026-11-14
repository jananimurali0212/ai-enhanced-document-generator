"""
Supabase Service module.
Manages Supabase client lifecycle, user-authenticated RLS-scoped clients,
and graceful connection diagnostics.
"""

import logging
from typing import Optional
from supabase import create_client, Client, ClientOptions
from app.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self._anon_client: Optional[Client] = None
        self._admin_client: Optional[Client] = None

    @property
    def is_available(self) -> bool:
        return settings.is_supabase_configured

    def get_anon_client(self) -> Optional[Client]:
        """Returns the public anonymous Supabase client."""
        if not self.is_available:
            return None
        if self._anon_client is None:
            try:
                self._anon_client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ANON_KEY
                )
            except Exception as e:
                logger.error(f"Failed to create Supabase anon client: {e}")
                return None
        return self._anon_client

    def get_user_client(self, access_token: str) -> Optional[Client]:
        """
        Returns a Supabase client scoped to the authenticated user's access token.
        Ensures all PostgREST operations strictly adhere to Row Level Security (RLS).
        """
        if not self.is_available:
            return None
        try:
            options = ClientOptions(
                headers={"Authorization": f"Bearer {access_token}"}
            )
            client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_ANON_KEY,
                options=options
            )
            # Also attach authorization header to postgrest directly
            if hasattr(client, "postgrest"):
                client.postgrest.auth(access_token)
            return client
        except Exception as e:
            logger.error(f"Failed to create user-scoped Supabase client: {e}")
            return None

    def get_admin_client(self) -> Optional[Client]:
        """Returns service-role admin client (restricted to system migrations/admin tasks)."""
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            return None
        if self._admin_client is None:
            try:
                self._admin_client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_ROLE_KEY
                )
            except Exception as e:
                logger.error(f"Failed to create Supabase admin client: {e}")
                return None
        return self._admin_client

    def check_connection(self) -> dict:
        """Verifies connectivity to Supabase."""
        if not self.is_available:
            return {
                "configured": False,
                "status": "not_configured",
                "message": "SUPABASE_URL or SUPABASE_ANON_KEY missing in environment."
            }
        try:
            client = self.get_anon_client()
            if not client:
                return {"configured": True, "status": "error", "message": "Client initialization failed."}
            return {"configured": True, "status": "connected", "url": settings.SUPABASE_URL}
        except Exception as e:
            return {"configured": True, "status": "error", "message": str(e)}

# Global singleton
supabase_service = SupabaseService()
