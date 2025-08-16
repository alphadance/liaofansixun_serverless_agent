import json
import logging
import os
import uuid
from http import HTTPStatus

from dashscope import Application

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
MAX_INPUT_LENGTH = 500
MIN_INPUT_LENGTH = 1

# Environment configuration
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
APP_ID = os.getenv('BAILIAN_AGENT_ID', '')


def error_response(status_code, error_msg, request_id=None):
    """Generate standardized error response."""
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    if request_id:
        headers['X-Request-ID'] = request_id
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps({'error': error_msg}, ensure_ascii=False)
    }


def success_response(data, request_id):
    """Generate standardized success response."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Request-ID': request_id
        },
        'body': json.dumps(data, ensure_ascii=False)
    }


def parse_event(event):
    """Parse and normalize the event into a standard format."""
    # Handle different input formats
    if isinstance(event, bytes):
        event = json.loads(event.decode('utf-8'))
    elif isinstance(event, str):
        event = json.loads(event)
    elif not isinstance(event, dict):
        raise ValueError(f"Unexpected event type: {type(event)}")
    
    # Detect request type and normalize
    if 'httpMethod' in event:
        # HTTP trigger format
        return {
            'method': event.get('httpMethod', 'GET'),
            'path': event.get('path', '/'),
            'body': event.get('body', '{}'),
            'headers': event.get('headers', {})
        }
    elif 'input' in event:
        # Direct invocation format (console test)
        return {
            'method': 'POST',
            'path': '/process',
            'body': json.dumps({'user_input': event['input']}),
            'headers': {}
        }
    else:
        raise ValueError("Unknown event format")


def validate_configuration():
    """Validate required configuration."""
    errors = []
    
    if not DASHSCOPE_API_KEY:
        errors.append("Missing DASHSCOPE_API_KEY")
    
    if not APP_ID:
        errors.append("Missing BAILIAN_AGENT_ID")
    
    if errors:
        raise ValueError(f"Configuration error: {', '.join(errors)}")


def parse_request_body(body_str):
    """Parse and validate request body."""
    try:
        body = json.loads(body_str)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in request body")
    
    user_input = body.get('user_input', '').strip()
    if not user_input:
        raise ValueError("user_input is required")
    
    if len(user_input) < MIN_INPUT_LENGTH or len(user_input) > MAX_INPUT_LENGTH:
        raise ValueError(f"user_input must be {MIN_INPUT_LENGTH}-{MAX_INPUT_LENGTH} characters")
    
    session_id = body.get('session_id') or str(uuid.uuid4())
    
    return user_input, session_id


def call_dashscope_api(user_input, session_id):
    """Call DashScope API and return response."""
    kwargs = {
        'api_key': DASHSCOPE_API_KEY,
        'app_id': APP_ID,
        'prompt': user_input,
        'session_id': session_id
    }
    
    response = Application.call(**kwargs)
    
    # Handle API errors
    if response.status_code != HTTPStatus.OK:
        logger.error(f"DashScope API error: code={response.status_code}, message={response.message}")
        
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            raise Exception("Authentication failed")
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise Exception("Rate limit exceeded")
        else:
            raise Exception(f"Agent service error: {response.message}")
    
    return response


def handler(event, context):
    """
    Alibaba Cloud Function Compute handler for DashScope API.
    
    Args:
        event: FC event containing HTTP request data
        context: FC context object
        
    Returns:
        dict: HTTP response for FC
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Parse and normalize event
        request = parse_event(event)
        
        # Update request ID if provided in headers
        if 'X-Request-ID' in request['headers']:
            request_id = request['headers']['X-Request-ID']
        
        # Handle health check
        if request['path'] == '/health' and request['method'] == 'GET':
            return success_response({'status': 'healthy'}, request_id)
        
        # Handle process endpoint
        if request['path'] == '/process' and request['method'] == 'POST':
            # Validate configuration
            validate_configuration()
            
            # Parse request body
            user_input, session_id = parse_request_body(request['body'])
            
            # Call DashScope API
            response = call_dashscope_api(user_input, session_id)
            
            # Parse the agent's JSON response
            try:
                agent_response = json.loads(response.output.text)
                # Return the parsed JSON directly with metadata
                response_data = {
                    **agent_response,
                    '_metadata': {
                        'session_id': response.output.session_id,
                        'request_id': response.request_id
                    }
                }
            except json.JSONDecodeError:
                # Fallback if response is not valid JSON
                response_data = {
                    'text': response.output.text,
                    'session_id': response.output.session_id,
                    'request_id': response.request_id
                }
            
            return success_response(response_data, request_id)
        
        # Path not found
        return error_response(404, 'Not found', request_id)
        
    except ValueError as e:
        # Client errors (400)
        return error_response(400, str(e), request_id)
    
    except Exception as e:
        # Server errors (500)
        logger.error(f"Handler error: {str(e)}")
        return error_response(500, 'Internal server error', request_id)