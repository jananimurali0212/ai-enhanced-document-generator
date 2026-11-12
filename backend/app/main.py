from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="AI-Enhanced Document Generator API",
    description="Backend API providing template metadata, AI document generation shells, and reference document grounding.",
    version="0.1.0"
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
        "health": "/api/health"
    }
