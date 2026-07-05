"""
Network/Connections API routes
Handles user connections and networking
"""
from flask import Blueprint, jsonify, request, session
from api.middleware.auth import login_required
from database.models import db, User, Post, Connection

network_bp = Blueprint('network', __name__, url_prefix='/api')


@network_bp.route('/network')
@login_required
def network():
    """Get network users with connection status"""
    me = session['user_id']
    role_filter = request.args.get('role')
    
    q = User.query.filter(User.id != me, User.role != 'Admin')
    if role_filter:
        q = q.filter_by(role=role_filter)
    
    users = q.all()
    
    result = []
    for u in users:
        d = u.to_dict()
        
        # Check connection status
        conn = Connection.query.filter(
            ((Connection.requester_id == me) & (Connection.receiver_id == u.id)) |
            ((Connection.requester_id == u.id) & (Connection.receiver_id == me))
        ).first()
        
        d['conn_status'] = conn.status if conn else None
        d['conn_is_mine'] = (conn.requester_id == me) if conn else False
        d['post_count'] = Post.query.filter_by(user_id=u.id).count()
        result.append(d)
    
    return jsonify(result), 200


@network_bp.route('/connect/<int:uid>', methods=['POST'])
@login_required
def connect(uid):
    """Send, accept, or cancel connection request"""
    me = session['user_id']
    
    if me == uid:
        return jsonify({'message': 'Cannot connect to yourself'}), 400
    
    data = request.get_json() or {}
    action = data.get('action', 'request')  # request | accept | cancel
    
    conn = Connection.query.filter(
        ((Connection.requester_id == me) & (Connection.receiver_id == uid)) |
        ((Connection.requester_id == uid) & (Connection.receiver_id == me))
    ).first()
    
    if action == 'request':
        if conn:
            return jsonify({'message': 'Connection already exists'}), 409
        new_conn = Connection(requester_id=me, receiver_id=uid, status='pending')
        db.session.add(new_conn)
        db.session.commit()
        return jsonify({'status': 'pending'}), 201
    
    if action == 'accept' and conn and conn.receiver_id == me:
        conn.status = 'accepted'
        db.session.commit()
        return jsonify({'status': 'accepted'}), 200
    
    if action == 'cancel' and conn:
        db.session.delete(conn)
        db.session.commit()
        return jsonify({'status': 'removed'}), 200
    
    return jsonify({'message': 'Invalid action'}), 400
