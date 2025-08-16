import json
import logging
import os
import uuid
from http import HTTPStatus

from dashscope import Application

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment configuration
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
APP_ID = os.getenv('BAILIAN_AGENT_ID', '')


def handler(event, context):
    """
    Alibaba Cloud Function Compute handler for DashScope API.
    
    Args:
        event: FC event containing HTTP request data
        context: FC context object
        
    Returns:
        dict: HTTP response for FC
    """
    try:
        # Parse HTTP method
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # Handle health check
        if path == '/health' and http_method == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'healthy'})
            }
        
        # Handle process endpoint
        if path == '/process' and http_method == 'POST':
            # Parse request body
            try:
                body = json.loads(event.get('body', '{}'))
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Invalid JSON'})
                }
            
            # Validate input
            user_input = body.get('user_input', '').strip()
            if not user_input or len(user_input) < 1 or len(user_input) > 500:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'user_input is required and must be 1-500 characters'})
                }
            
            # Get or generate session_id
            session_id = body.get('session_id') or str(uuid.uuid4())
            
            # Get request ID from headers
            headers = event.get('headers', {})
            request_id = headers.get('X-Request-ID', str(uuid.uuid4()))
            
            # Call DashScope API
            try:
                kwargs = {
                    'api_key': DASHSCOPE_API_KEY,
                    'app_id': APP_ID,
                    'prompt': user_input,
                    'session_id': session_id
                }
                
                response = Application.call(**kwargs)
                
                # Handle API errors
                if response.status_code != HTTPStatus.OK:
                    logger.error(
                        f"DashScope API error: code={response.status_code}, message={response.message}"
                    )
                    
                    if response.status_code == HTTPStatus.UNAUTHORIZED:
                        status_code = 401
                        error_msg = "Authentication failed"
                    elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                        status_code = 429
                        error_msg = "Rate limit exceeded"
                    else:
                        status_code = 502
                        error_msg = "Agent service error"
                    
                    return {
                        'statusCode': status_code,
                        'headers': {
                            'Content-Type': 'application/json',
                            'X-Request-ID': request_id
                        },
                        'body': json.dumps({
                            'error': error_msg,
                            'code': getattr(response, 'code', ''),
                            'message': response.message
                        })
                    }
                
                # Return successful response
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'X-Request-ID': request_id
                    },
                    'body': json.dumps({
                        'text': response.output.text,
                        'session_id': response.output.session_id,
                        'request_id': response.request_id
                    })
                }
                
            except Exception as e:
                logger.error(f"Unexpected error calling DashScope: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'X-Request-ID': request_id
                    },
                    'body': json.dumps({'error': 'Internal server error'})
                }
        
        # Method not allowed
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Not found'})
        }
        
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }