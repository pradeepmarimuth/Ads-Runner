"""
Marketing AI Platform - Main Application
Refactored modular architecture with Blueprint-based routing
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from backend.config import get_config
from database.models import db
from api.services.ollama_service import OllamaService
from api.services.seed_service import seed_system

# Import blueprints
from api.routes.auth import auth_bp
from api.routes.views import views_bp
from api.routes.profile import profile_bp
from api.routes.posts import posts_bp
from api.routes.network import network_bp
from api.routes.messages import messages_bp
from api.routes.campaigns import campaigns_bp
from api.routes.ai import ai_bp
from api.routes.admin import admin_bp


def create_app(config_name=None):
    """Application factory"""
    app = Flask(
        __name__,
        template_folder='../frontend/templates',
        static_folder='../frontend/static'
    )
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(network_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(admin_bp)
    
    # Create tables and seed data
    with app.app_context():
        db.create_all()
        seed_system()
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)
