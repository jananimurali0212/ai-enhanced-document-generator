# Routes package
from app.routes.documents import router as documents_router
from app.routes.export import router as export_router
from app.routes.quality import router as quality_router

__all__ = ["documents_router", "export_router", "quality_router"]
