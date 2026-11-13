from typing import Optional

class AIServiceException(Exception):
    """Base exception for all AI-related errors."""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_type: str = "AI_SERVICE_ERROR",
        retry_guidance: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.retry_guidance = retry_guidance

class AIConfigurationException(AIServiceException):
    def __init__(
        self,
        message: str = "Gemini API key is not configured or is invalid. Set GEMINI_API_KEY in backend/.env.",
        retry_guidance: str = "Configure your GEMINI_API_KEY in the backend .env file. Obtain one at https://aistudio.google.com/."
    ):
        super().__init__(
            message=message,
            status_code=503,
            error_type="AI_CONFIGURATION_ERROR",
            retry_guidance=retry_guidance
        )

class AIRateLimitException(AIServiceException):
    def __init__(
        self,
        message: str = "Gemini API rate limit or quota exceeded.",
        retry_guidance: str = "The model is currently rate-limited. Please wait 15 to 30 seconds before resubmitting your request."
    ):
        super().__init__(
            message=message,
            status_code=429,
            error_type="AI_RATE_LIMIT_EXCEEDED",
            retry_guidance=retry_guidance
        )

class AITimeoutException(AIServiceException):
    def __init__(
        self,
        message: str = "Request to Gemini API timed out.",
        retry_guidance: str = "The generation request timed out. Try reducing requested length or splitting the content, then retry."
    ):
        super().__init__(
            message=message,
            status_code=504,
            error_type="AI_TIMEOUT",
            retry_guidance=retry_guidance
        )

class AIGenerationException(AIServiceException):
    def __init__(
        self,
        message: str = "AI output generation failed or returned empty content.",
        retry_guidance: str = "Please verify your input prompt and constraints, or try again with a slightly different wording."
    ):
        super().__init__(
            message=message,
            status_code=502,
            error_type="AI_GENERATION_FAILED",
            retry_guidance=retry_guidance
        )

