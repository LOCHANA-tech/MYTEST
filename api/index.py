import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from the parent directory
from app import app

# This is the entry point for Vercel serverless functions
# Vercel will automatically call this function with the request
def handler(environ, start_response):
    """Vercel serverless function handler"""
    return app(environ, start_response)

# For local testing
if __name__ == "__main__":
    app.run(debug=True)
