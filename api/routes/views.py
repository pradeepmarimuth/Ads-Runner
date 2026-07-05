"""
View routes
Handles all HTML page rendering
"""
from flask import Blueprint, render_template, redirect, url_for, session
from api.middleware.auth import login_required, admin_required
from database.models import db, User, Message, Connection

views_bp = Blueprint('views', __name__)


@views_bp.route('/favicon.ico')
def favicon():
    """Favicon handler"""
    return '', 204


@views_bp.route('/')
@login_required
def home():
    """Home/Dashboard page"""
    if session.get('role') == 'Admin':
        return redirect(url_for('views.admin'))
    
    user = User.query.get(session['user_id'])
    unread = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return render_template('home.html', user=user, unread=unread)


@views_bp.route('/feed')
@login_required
def feed():
    """Social feed page"""
    user = User.query.get(session['user_id'])
    unread = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return render_template('feed.html', user=user, unread=unread)


@views_bp.route('/network')
@login_required
def network():
    """Network/Connections page"""
    user = User.query.get(session['user_id'])
    unread = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return render_template('network.html', user=user, unread=unread)


@views_bp.route('/profile/<int:uid>')
@login_required
def profile(uid):
    """User profile page"""
    me = User.query.get(session['user_id'])
    them = User.query.get_or_404(uid)
    unread = Message.query.filter_by(receiver_id=me.id, is_read=False).count()
    
    # Check connection status
    conn = Connection.query.filter(
        ((Connection.requester_id == me.id) & (Connection.receiver_id == uid)) |
        ((Connection.requester_id == uid) & (Connection.receiver_id == me.id))
    ).first()
    
    conn_status = conn.status if conn else None
    conn_is_mine = conn.requester_id == me.id if conn else False
    
    return render_template(
        'profile.html',
        user=me,
        profile=them,
        unread=unread,
        conn_status=conn_status,
        conn_is_mine=conn_is_mine
    )


@views_bp.route('/profile/edit')
@login_required
def profile_edit():
    """Profile edit page"""
    user = User.query.get(session['user_id'])
    return render_template('profile_edit.html', user=user)


@views_bp.route('/messages')
@login_required
def messages():
    """Messages inbox page"""
    user = User.query.get(session['user_id'])
    return render_template('messages.html', user=user, chat_user=None, chat_user_id=None)


@views_bp.route('/messages/<int:uid>')
@login_required
def messages_thread(uid):
    """Messages thread with specific user"""
    me = User.query.get(session['user_id'])
    chat_usr = User.query.get_or_404(uid)
    
    # Mark received messages as read
    Message.query.filter_by(
        sender_id=uid,
        receiver_id=me.id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()
    
    return render_template('messages.html', user=me, chat_user=chat_usr, chat_user_id=uid)


@views_bp.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard page"""
    user = User.query.get(session['user_id'])
    unread = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return render_template('analytics.html', user=user, unread=unread)


@views_bp.route('/campaigns')
@login_required
def campaigns():
    """Campaigns management page"""
    if session.get('role') == 'Admin':
        return redirect(url_for('views.admin'))
    
    user = User.query.get(session['user_id'])
    unread = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return render_template('campaigns.html', username=user.name, unread=unread)


@views_bp.route('/ai')
@login_required
def ai():
    """AI workspace page"""
    if session.get('role') == 'Admin':
        return redirect(url_for('views.admin'))
    
    user = User.query.get(session['user_id'])
    unread = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return render_template('ai.html', username=user.name, unread=unread)


@views_bp.route('/admin')
@login_required
@admin_required
def admin():
    """Admin dashboard page"""
    return render_template('admin.html', username=session.get('username'))
