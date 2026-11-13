from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.core.exceptions import AIServiceException

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API providing template metadata, Gemini-powered AI document generation, rewriting, summarization, and expansion.",
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
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "message": "AI-Enhanced Document Generator Backend is running.",
        "documentation": "/docs",
        "health": "/api/health",
        "version": settings.VERSION,
        "is_gemini_configured": settings.is_gemini_configured
    }
