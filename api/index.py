import os
import sys
from werkzeug.wrappers import Request, Response

# Add the parent directory to Python path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects a WSGI application, not a handler function
# This makes the Flask app compatible with Vercel's Python runtime
application = app

# For local testing
if __name__ == '__main__':
    app.run(debug=True)
