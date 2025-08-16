import json
import logging
from fastapi import Request
from app import app, ProcessRequest

logger = logging.getLogger()


async def handler(event, context):
    """
    Alibaba Cloud Function Compute handler for FastAPI app.
    
    Args:
        event: FC event containing HTTP request data
        context: FC context object
        
    Returns:
        dict: HTTP response for FC
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Validate input
        request_data = ProcessRequest(**body)
        
        # Create mock Request object for FastAPI
        headers = event.get('headers', {})
        mock_request = type('Request', (), {
            'headers': type('Headers', (), {
                'get': lambda self, key, default=None: headers.get(key, default)
            })()
        })()
        
        # Call the FastAPI handler directly
        response = await app.process_request(request_data, mock_request)
        
        # Return FC-compatible response
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.body.decode('utf-8') if hasattr(response.body, 'decode') else str(response.body)
        }
        
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'user_input is required and must be 1-500 characters'})
        }