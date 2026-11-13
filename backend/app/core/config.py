import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Search for .env in current backend dir or project root
base_dir = Path(__file__).resolve().parent.parent.parent
env_paths = [
    base_dir / ".env",
    base_dir.parent / ".env",
    Path(".env").resolve()
]

for p in env_paths:
    if p.exists():
        load_dotenv(dotenv_path=p)
        break
else:
    load_dotenv()  # Fallback to standard environment lookup

class Settings:
    PROJECT_NAME: str = "AI-Enhanced Document Generator"
    VERSION: str = "0.2.0"
    API_V1_STR: str = "/api"

    # Gemini API Credentials (strictly backend; never sent to frontend)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Model Hyperparameters
    TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    MAX_OUTPUT_TOKENS: int = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "4096"))
    TIMEOUT_SECONDS: int = int(os.getenv("AI_REQUEST_TIMEOUT", "60"))

    # Mock fallback flag (if true and key is absent, use high-fidelity mock generator)
    ALLOW_MOCK_FALLBACK: bool = os.getenv("ALLOW_MOCK_FALLBACK", "true").lower() in ("true", "1", "yes")

    @property
    def is_gemini_configured(self) -> bool:
        return bool(self.GEMINI_API_KEY and not self.GEMINI_API_KEY.startswith("your_gemini_api_key"))

settings = Settings()

