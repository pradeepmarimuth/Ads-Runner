"""
WSGI entry point for production deployment
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app as application

if __name__ == "__main__":
    application.run()
