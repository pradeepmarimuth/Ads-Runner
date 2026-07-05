"""
API Routes package initialization
"""
from .auth import auth_bp
from .views import views_bp
from .profile import profile_bp
from .posts import posts_bp
from .network import network_bp
from .messages import messages_bp
from .campaigns import campaigns_bp
from .ai import ai_bp
from .admin import admin_bp

__all__ = [
    'auth_bp',
    'views_bp',
    'profile_bp',
    'posts_bp',
    'network_bp',
    'messages_bp',
    'campaigns_bp',
    'ai_bp',
    'admin_bp'
]
