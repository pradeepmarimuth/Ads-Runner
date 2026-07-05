"""
API package initialization
"""
from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import routes after blueprint creation to avoid circular imports
from api.routes import auth, posts, campaigns, messages, network, ai, admin

__all__ = ['api_bp']
