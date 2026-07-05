"""
Posts/Feed API routes
Handles posts, likes, comments
"""
from flask import Blueprint, jsonify, request, session
from api.middleware.auth import login_required
from database.models import db, Post, PostLike, Comment

posts_bp = Blueprint('posts', __name__, url_prefix='/api')


@posts_bp.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    """Get all posts or create new post"""
    if request.method == 'GET':
        posts = Post.query.order_by(Post.timestamp.desc()).limit(50).all()
        return jsonify([p.to_dict() for p in posts]), 200
    
    data = request.get_json() or {}
    content = data.get('content', '').strip()
    image_url = data.get('image_url', '').strip()
    reel_url = data.get('reel_url', '').strip()
    
    if not content and not image_url and not reel_url:
        return jsonify({'message': 'Content is required'}), 400
    
    p = Post(
        user_id=session['user_id'],
        content=content or '📸',
        image_url=image_url or None,
        reel_url=reel_url or None
    )
    db.session.add(p)
    db.session.commit()
    
    return jsonify(p.to_dict()), 201


@posts_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@login_required
def post_like(post_id):
    """Like or unlike a post"""
    p = Post.query.get_or_404(post_id)
    uid = session['user_id']
    existing = PostLike.query.filter_by(post_id=post_id, user_id=uid).first()
    
    if existing:
        # Unlike
        db.session.delete(existing)
        p.likes_count = max(0, p.likes_count - 1)
        db.session.commit()
        return jsonify({'likes_count': p.likes_count, 'liked': False}), 200
    else:
        # Like
        like = PostLike(post_id=post_id, user_id=uid)
        db.session.add(like)
        p.likes_count += 1
        db.session.commit()
        return jsonify({'likes_count': p.likes_count, 'liked': True}), 200


@posts_bp.route('/posts/<int:post_id>/comments', methods=['GET', 'POST'])
@login_required
def post_comments(post_id):
    """Get comments for a post or add new comment"""
    Post.query.get_or_404(post_id)  # Ensure post exists
    
    if request.method == 'GET':
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.timestamp.asc()).all()
        return jsonify([c.to_dict() for c in comments]), 200
    
    data = request.get_json() or {}
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'message': 'Comment cannot be empty'}), 400
    
    c = Comment(post_id=post_id, user_id=session['user_id'], content=content)
    db.session.add(c)
    db.session.commit()
    
    return jsonify(c.to_dict()), 201


@posts_bp.route('/posts/<int:post_id>/liked', methods=['GET'])
@login_required
def post_liked(post_id):
    """Check if current user liked a post"""
    uid = session['user_id']
    liked = PostLike.query.filter_by(post_id=post_id, user_id=uid).first() is not None
    return jsonify({'liked': liked}), 200
