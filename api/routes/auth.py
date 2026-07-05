"""
Authentication routes
Handles login, signup, logout
"""
from flask import Blueprint, render_template, request, session, redirect, url_for
from database.models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return redirect(url_for('views.home'))
        else:
            session.clear()
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        pwd = request.form.get('password', '').strip()
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(pwd):
            session.update({
                'user_id': user.id,
                'username': user.name,
                'role': user.role
            })
            return redirect(
                url_for('views.admin') if user.role == 'Admin'
                else url_for('views.home')
            )
        
        return render_template('login.html', error='Invalid credentials.')
    
    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page and registration"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return redirect(url_for('views.home'))
        else:
            session.clear()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        pwd = request.form.get('password', '').strip()
        role = request.form.get('role', 'Customer').strip()
        tagline = request.form.get('tagline', '').strip()
        
        if not name or not email or not pwd:
            return render_template('signup.html', error='All fields are required.')
        
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already registered.')
        
        u = User(
            name=name,
            email=email,
            role=role,
            tagline=tagline or f'Anti-Gravity {role}'
        )
        u.set_password(pwd)
        db.session.add(u)
        db.session.commit()
        
        # Seed campaigns for new customers
        if role == 'Customer':
            from api.services.seed_service import seed_campaigns
            seed_campaigns(u.id)
        
        session.update({
            'user_id': u.id,
            'username': u.name,
            'role': u.role
        })
        
        return redirect(
            url_for('views.admin') if role == 'Admin'
            else url_for('views.home')
        )
    
    return render_template('signup.html')


@auth_bp.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('auth.login'))
