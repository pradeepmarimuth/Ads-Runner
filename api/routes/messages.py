"""
Messages API routes
Handles messaging between users
"""
from flask import Blueprint, jsonify, request, session
from api.middleware.auth import login_required
from database.models import db, User, Message

messages_bp = Blueprint('messages', __name__, url_prefix='/api')


@messages_bp.route('/messages/inbox')
@login_required
def inbox():
    """Get inbox with all message threads"""
    me = session['user_id']
    
    # Find all users I've exchanged messages with
    sent_ids = db.session.query(Message.receiver_id).filter_by(sender_id=me).distinct()
    recv_ids = db.session.query(Message.sender_id).filter_by(receiver_id=me).distinct()
    partner_ids = set([r[0] for r in sent_ids] + [r[0] for r in recv_ids])
    
    inbox = []
    for pid in partner_ids:
        partner = User.query.get(pid)
        if not partner:
            continue
        
        last_msg = Message.query.filter(
            ((Message.sender_id == me) & (Message.receiver_id == pid)) |
            ((Message.sender_id == pid) & (Message.receiver_id == me))
        ).order_by(Message.timestamp.desc()).first()
        
        unread_count = Message.query.filter_by(
            sender_id=pid,
            receiver_id=me,
            is_read=False
        ).count()
        
        inbox.append({
            'partner_id': partner.id,
            'partner_name': partner.name,
            'partner_role': partner.role,
            'partner_avatar': partner.avatar_url or '',
            'last_message': last_msg.content[:60] if last_msg else '',
            'last_ts': last_msg.timestamp.strftime('%H:%M') if last_msg else '',
            'unread': unread_count
        })
    
    # Sort by last message time
    inbox.sort(key=lambda x: x['last_ts'], reverse=True)
    return jsonify(inbox), 200


@messages_bp.route('/messages/<int:uid>', methods=['GET', 'POST'])
@login_required
def messages_thread(uid):
    """Get or send messages in a thread"""
    me = session['user_id']
    
    if request.method == 'GET':
        msgs = Message.query.filter(
            ((Message.sender_id == me) & (Message.receiver_id == uid)) |
            ((Message.sender_id == uid) & (Message.receiver_id == me))
        ).order_by(Message.timestamp.asc()).all()
        
        # Mark as read
        Message.query.filter_by(
            sender_id=uid,
            receiver_id=me,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()
        
        return jsonify([m.to_dict() for m in msgs]), 200
    
    data = request.get_json() or {}
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'message': 'Empty message'}), 400
    
    m = Message(sender_id=me, receiver_id=uid, content=content)
    db.session.add(m)
    db.session.commit()
    
    return jsonify(m.to_dict()), 201


@messages_bp.route('/messages/unread-count')
@login_required
def unread_count():
    """Get unread message count"""
    count = Message.query.filter_by(
        receiver_id=session['user_id'],
        is_read=False
    ).count()
    return jsonify({'count': count}), 200
