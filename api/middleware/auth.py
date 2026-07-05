"""
Authentication middleware
"""
from functools import wraps
from flask import session, redirect, url_for, jsonify, request
from database.models import User


def login_required(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'message': 'Unauthenticated'}), 401
            return redirect(url_for('auth.login'))
        
        # Ensure user exists in the database
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            if request.path.startswith('/api/'):
                return jsonify({'message': 'Unauthenticated'}), 401
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return wrap


def admin_required(f):
    """Decorator to require admin role for a route"""
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('role') != 'Admin':
            return redirect(url_for('views.home'))
        return f(*args, **kwargs)
    return wrap
