import logging
import os
import uuid

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

# Type aliases
Headers = dict[str, str]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment configuration
BAILIAN_AGENT_ID = os.getenv('BAILIAN_AGENT_ID', '')
BAILIAN_API_URL = os.getenv(
    'BAILIAN_API_URL', 
    f'https://bailian.aliyuncs.com/v1/agents/{BAILIAN_AGENT_ID}/invoke' if BAILIAN_AGENT_ID else ''
)
BAILIAN_API_KEY = os.getenv('BAILIAN_API_KEY', '')
PORT = int(os.getenv('PORT', '8000'))

# Validate required environment variables
if not BAILIAN_API_KEY:
    logger.warning("BAILIAN_API_KEY not set - API calls will fail")
if not BAILIAN_API_URL:
    logger.warning("BAILIAN_API_URL not configured - API calls will fail")

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
    
    @validator('user_input')
    def validate_user_input(cls, v: str) -> str:
        """Ensure user_input is properly trimmed."""
        return v.strip()


@app.on_event("startup")
async def startup_event() -> None:
    """Log server startup."""
    logger.info(f"Starting proxy server on port {PORT}")
    logger.info(f"Bailian API URL: {BAILIAN_API_URL}")


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
        request_data: Validated request containing user_input.
        request: FastAPI request object for headers.
        
    Returns:
        Response: Raw response from Bailian API or error response.
    """
    # Extract or generate request ID for tracing
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    
    # Prepare headers for Bailian API
    headers: Headers = {
        'Authorization': f'Bearer {BAILIAN_API_KEY}',
        'Content-Type': 'application/json',
        'X-Request-ID': request_id
    }
    
    # Prepare request body
    payload: dict[str, str] = {
        'input': request_data.user_input
    }
    
    # Create async client with timeout
    async with httpx.AsyncClient(timeout=httpx.Timeout(8.0)) as client:
        try:
            # Call Bailian API
            response = await client.post(
                BAILIAN_API_URL,
                json=payload,
                headers=headers
            )
            
            # Forward successful responses unchanged
            if response.status_code == 200:
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers={
                        'Content-Type': response.headers.get('Content-Type', 'application/json'),
                        'X-Request-ID': request_id
                    }
                )
            
            # Forward non-200 responses from Bailian
            logger.error(
                f"Bailian API returned status {response.status_code} for request {request_id}"
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={
                    'Content-Type': response.headers.get('Content-Type', 'application/json'),
                    'X-Request-ID': request_id
                }
            )
            
        except httpx.TimeoutException:
            logger.error(f"Bailian API timeout for request {request_id}")
            return JSONResponse(
                status_code=504,
                content={"error": "Agent processing timed out"},
                headers={'X-Request-ID': request_id}
            )
            
        except httpx.NetworkError as e:
            logger.error(f"Network error calling Bailian API for request {request_id}: {str(e)}")
            return JSONResponse(
                status_code=502,
                content={"error": "Agent service unreachable"},
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


@app.exception_handler(HTTPException)
async def http_exception_handler(req: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )