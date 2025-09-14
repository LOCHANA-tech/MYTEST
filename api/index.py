import os
import sys
from werkzeug.wrappers import Request, Response
from werkzeug.serving import WSGIRequestHandler
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import HTTPException, NotFound, InternalServerError
import json

# Add the parent directory to Python path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

def handler(request):
    """
    Vercel serverless function handler for Flask application
    """
    # Create a WSGI environment from the request
    environ = {
        'REQUEST_METHOD': request.method,
        'PATH_INFO': request.path,
        'QUERY_STRING': request.query_string.decode('utf-8'),
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8000',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'CONTENT_TYPE': request.headers.get('Content-Type', ''),
        'CONTENT_LENGTH': request.headers.get('Content-Length', ''),
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': request.body,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    # Add headers to environment
    for key, value in request.headers.items():
        key = key.upper().replace('-', '_')
        if key not in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
            environ[f'HTTP_{key}'] = value

    # Create response collector
    response_data = {
        'status': None,
        'headers': [],
        'body': b''
    }

    def start_response(status, response_headers, exc_info=None):
        response_data['status'] = status
        response_data['headers'] = response_headers
        return response_data['body'].write

    # Get response from Flask app
    app_iter = app(environ, start_response)
    
    # Collect response body
    for chunk in app_iter:
        if isinstance(chunk, str):
            response_data['body'] += chunk.encode('utf-8')
        else:
            response_data['body'] += chunk

    # Parse status code
    status_code = int(response_data['status'].split(' ')[0])

    # Create response object
    response = Response(
        response=response_data['body'],
        status=status_code,
        headers=dict(response_data['headers'])
    )

    return response

# For local testing
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 8000, handler, use_reloader=True)
