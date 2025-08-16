import logging
import os
import uuid
from http import HTTPStatus

import uvicorn
from dashscope import Application
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment configuration
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
APP_ID = os.getenv('BAILIAN_AGENT_ID', '')
PORT = int(os.getenv('PORT', '8000'))

# Validate required environment variables
if not DASHSCOPE_API_KEY:
    logger.warning("DASHSCOPE_API_KEY not set - API calls will fail")
if not APP_ID:
    logger.warning("BAILIAN_AGENT_ID not set - API calls will fail")

# Initialize FastAPI app
app = FastAPI(
    title="Liao Fan Si Xun Proxy Server",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)


class ProcessRequest(BaseModel):
    """Request model for /process endpoint."""
    user_input: str = Field(..., min_length=1, max_length=500)
    session_id: str | None = Field(None, description="Optional session ID for conversation continuity")
    
    @validator('user_input')
    def validate_user_input(cls, v: str) -> str:
        """Ensure user_input is properly trimmed."""
        return v.strip()


@app.on_event("startup")
async def startup_event() -> None:
    """Log server startup."""
    logger.info(f"Starting proxy server on port {PORT}")
    logger.info(f"Bailian App ID: {APP_ID}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Log server shutdown."""
    logger.info("Shutting down proxy server")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.post("/process")
async def process_request(
    request_data: ProcessRequest,
    request: Request
) -> Response:
    """
    Forward user input to Bailian agent API and return response.
    
    Args:
        request_data: Validated request containing user_input and optional session_id.
        request: FastAPI request object for headers.
        
    Returns:
        Response: Response from Bailian API or error response.
    """
    # Extract or generate request ID for tracing
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    
    try:
        # Call DashScope Application API
        kwargs = {
            'api_key': DASHSCOPE_API_KEY,
            'app_id': APP_ID,
            'prompt': request_data.user_input
        }
        
        # Use provided session_id or generate a new one
        session_id = request_data.session_id or str(uuid.uuid4())
        kwargs['session_id'] = session_id
            
        response = Application.call(**kwargs)
        
        # Handle API errors
        if response.status_code != HTTPStatus.OK:
            logger.error(
                f"DashScope API error for request {request_id}: "
                f"code={response.status_code}, message={response.message}"
            )
            
            # Map DashScope errors to appropriate HTTP status codes
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": "Authentication failed",
                        "code": response.code,
                        "message": response.message
                    },
                    headers={'X-Request-ID': request_id}
                )
            elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "code": response.code,
                        "message": response.message
                    },
                    headers={'X-Request-ID': request_id}
                )
            else:
                return JSONResponse(
                    status_code=502,
                    content={
                        "error": "Agent service error",
                        "code": response.code,
                        "message": response.message
                    },
                    headers={'X-Request-ID': request_id}
                )
        
        # Return successful response
        return JSONResponse(
            status_code=200,
            content={
                "text": response.output.text,
                "session_id": response.output.session_id,
                "request_id": response.request_id
            },
            headers={'X-Request-ID': request_id}
        )
        
    except Exception as e:
        logger.error(f"Unexpected error for request {request_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
            headers={'X-Request-ID': request_id}
        )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(req: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with proper error messages."""
    return JSONResponse(
        status_code=400,
        content={"error": "user_input is required and must be 1-500 characters"}
    )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )