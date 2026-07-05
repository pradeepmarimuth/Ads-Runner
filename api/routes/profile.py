"""
Profile API routes
Handles user profile operations
"""
import os
import datetime
from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
from api.middleware.auth import login_required
from database.models import db, User, Post, Connection

profile_bp = Blueprint('profile', __name__, url_prefix='/api')


@profile_bp.route('/profile/<int:uid>')
@login_required
def profile(uid):
    """Get user profile"""
    u = User.query.get_or_404(uid)
    data = u.to_dict()
    data['post_count'] = Post.query.filter_by(user_id=uid).count()
    data['network_count'] = Connection.query.filter(
        ((Connection.requester_id == uid) | (Connection.receiver_id == uid)),
        Connection.status == 'accepted'
    ).count()
    return jsonify(data), 200


@profile_bp.route('/profile/update', methods=['POST'])
@login_required
def profile_update():
    """Update user profile"""
    user = User.query.get(session['user_id'])
    data = request.get_json() or {}
    
    new_name = data.get('name', '').strip()
    if new_name and len(new_name) >= 2:
        user.name = new_name
        session['username'] = new_name
    
    user.bio = data.get('bio', user.bio)
    user.avatar_url = data.get('avatar_url', user.avatar_url)
    user.location = data.get('location', user.location)
    user.website = data.get('website', user.website)
    user.tagline = data.get('tagline', user.tagline)
    
    db.session.commit()
    return jsonify(user.to_dict()), 200


@profile_bp.route('/profile/delete', methods=['POST'])
@login_required
def profile_delete():
    """Delete user account"""
    user = User.query.get(session['user_id'])
    db.session.delete(user)
    db.session.commit()
    session.clear()
    return jsonify({'message': 'Account deleted successfully'}), 200


@profile_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload file (image/video)"""
    from flask import current_app
    
    if 'file' not in request.files:
        return jsonify({'message': 'No file in request'}), 400
    
    f = request.files['file']
    if not f or f.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
    if ext not in current_app.config['ALLOWED_EXTENSIONS']:
        return jsonify({'message': f'File type .{ext} not allowed'}), 400
    
    uid = session['user_id']
    ts = int(datetime.datetime.utcnow().timestamp())
    filename = secure_filename(f"{uid}_{ts}.{ext}")
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    f.save(os.path.join(upload_folder, filename))
    
    return jsonify({'url': f'/static/uploads/{filename}'}), 200
