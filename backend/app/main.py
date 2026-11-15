from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.routes.documents import router as documents_router
from app.routes.export import router as export_router
from app.routes.quality import router as quality_router
from app.core.config import settings
from app.core.exceptions import AIServiceException

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API providing template metadata, Gemini-powered AI document generation, persistent Supabase CRUD, PDF/DOCX exports, and AI Quality & Comparison analytics.",
    version=settings.VERSION
)

# Custom exception handler for structured AI error responses
@app.exception_handler(AIServiceException)
async def ai_service_exception_handler(request: Request, exc: AIServiceException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_type": exc.error_type,
            "retry_guidance": exc.retry_guidance
        }
    )

# Enable CORS for React Frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Register all route modules
app.include_router(router)
app.include_router(documents_router)
app.include_router(export_router)
app.include_router(quality_router)

@app.get("/")
def root():
    return {
        "message": "AI-Enhanced Document Generator Backend is running.",
        "documentation": "/docs",
        "health": "/api/health",
        "version": settings.VERSION,
        "is_gemini_configured": settings.is_gemini_configured,
        "is_supabase_configured": settings.is_supabase_configured
    }
