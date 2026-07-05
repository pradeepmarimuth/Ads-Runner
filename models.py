import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Valid roles in the platform
ROLES = ['Customer', 'Influencer', 'AdPublisher', 'Admin']

class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(100), unique=True, nullable=False)
    password      = db.Column(db.String(200), nullable=False)
    role          = db.Column(db.String(20), nullable=False, default='Customer')  # Customer | Influencer | AdPublisher | Admin

    # Profile fields
    bio           = db.Column(db.String(300), nullable=True)
    avatar_url    = db.Column(db.String(500), nullable=True)
    location      = db.Column(db.String(100), nullable=True)
    website       = db.Column(db.String(200), nullable=True)
    tagline       = db.Column(db.String(150), nullable=True)
    is_verified   = db.Column(db.Boolean, default=False)
    joined_at     = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    campaigns      = db.relationship('Campaign',    backref='owner',  lazy=True, cascade='all, delete-orphan')
    posts          = db.relationship('Post',        backref='author', lazy=True, cascade='all, delete-orphan')
    logs           = db.relationship('CampaignLog', backref='user',   lazy=True, cascade='all, delete-orphan')
    sent_messages  = db.relationship('Message', foreign_keys='Message.sender_id',   backref='sender',   lazy=True, cascade='all, delete-orphan')
    recv_messages  = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True, cascade='all, delete-orphan')
    sent_requests  = db.relationship('Connection', foreign_keys='Connection.requester_id', backref='requester', lazy=True, cascade='all, delete-orphan')
    recv_requests  = db.relationship('Connection', foreign_keys='Connection.receiver_id',  backref='target',    lazy=True, cascade='all, delete-orphan')
    comments       = db.relationship('Comment',    backref='commenter', lazy=True, cascade='all, delete-orphan')
    post_likes     = db.relationship('PostLike',   backref='liker',    lazy=True, cascade='all, delete-orphan')

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def avatar(self):
        return self.avatar_url or ''

    def role_badge_color(self):
        colors = {
            'Influencer':   'purple',
            'AdPublisher':  'cyan',
            'Customer':     'emerald',
            'Admin':        'pink'
        }
        return colors.get(self.role, 'slate')

    def to_dict(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'email':       self.email,
            'role':        self.role,
            'bio':         self.bio or '',
            'avatar_url':  self.avatar_url or '',
            'location':    self.location or '',
            'website':     self.website or '',
            'tagline':     self.tagline or '',
            'is_verified': self.is_verified,
            'joined_at':   self.joined_at.strftime('%Y-%m-%d') if self.joined_at else ''
        }


class Post(db.Model):
    __tablename__ = 'posts'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content     = db.Column(db.Text, nullable=False)
    image_url   = db.Column(db.String(500), nullable=True)
    reel_url    = db.Column(db.String(500), nullable=True)   # video URL for Reels
    likes_count = db.Column(db.Integer, default=0)
    timestamp   = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    # Relationships
    comments    = db.relationship('Comment',  backref='post', lazy=True, cascade='all, delete-orphan')
    post_likes  = db.relationship('PostLike', backref='post', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        author = self.author
        return {
            'id':            self.id,
            'user_id':       self.user_id,
            'username':      author.name if author else 'Unknown',
            'role':          author.role if author else '',
            'avatar_url':    author.avatar_url if author and author.avatar_url else '',
            'tagline':       author.tagline if author and author.tagline else '',
            'content':       self.content,
            'image_url':     self.image_url or '',
            'reel_url':      self.reel_url or '',
            'likes_count':   self.likes_count,
            'comment_count': len(self.comments),
            'timestamp':     self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }


class PostLike(db.Model):
    """Tracks which user liked which post — one like per user per post."""
    __tablename__ = 'post_likes'

    id      = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='uq_post_user_like'),)


class Comment(db.Model):
    __tablename__ = 'comments'

    id        = db.Column(db.Integer, primary_key=True)
    post_id   = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content   = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def to_dict(self):
        commenter = self.commenter
        return {
            'id':         self.id,
            'post_id':    self.post_id,
            'user_id':    self.user_id,
            'username':   commenter.name if commenter else 'Unknown',
            'role':       commenter.role if commenter else '',
            'avatar_url': commenter.avatar_url if commenter and commenter.avatar_url else '',
            'content':    self.content,
            'timestamp':  self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }


class Message(db.Model):
    __tablename__ = 'messages'

    id          = db.Column(db.Integer, primary_key=True)
    sender_id   = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content     = db.Column(db.Text, nullable=False)
    is_read     = db.Column(db.Boolean, default=False)
    timestamp   = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id':          self.id,
            'sender_id':   self.sender_id,
            'receiver_id': self.receiver_id,
            'content':     self.content,
            'is_read':     self.is_read,
            'timestamp':   self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }


class Connection(db.Model):
    __tablename__ = 'connections'

    id            = db.Column(db.Integer, primary_key=True)
    requester_id  = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    receiver_id   = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status        = db.Column(db.String(20), nullable=False, default='pending')  # pending | accepted
    created_at    = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id':           self.id,
            'requester_id': self.requester_id,
            'receiver_id':  self.receiver_id,
            'status':       self.status
        }


class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name        = db.Column(db.String(150), nullable=False)
    platform    = db.Column(db.String(50), nullable=False)
    spend       = db.Column(db.Float, nullable=False, default=0.0)
    revenue     = db.Column(db.Float, nullable=False, default=0.0)
    clicks      = db.Column(db.Integer, nullable=False, default=0)
    conversions = db.Column(db.Integer, nullable=False, default=0)
    date        = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            'id':          self.id,
            'user_id':     self.user_id,
            'name':        self.name,
            'platform':    self.platform,
            'spend':       self.spend,
            'revenue':     self.revenue,
            'clicks':      self.clicks,
            'conversions': self.conversions,
            'date':        self.date.strftime('%Y-%m-%d') if self.date else None
        }


class CampaignLog(db.Model):
    __tablename__ = 'campaign_logs'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    ad_link         = db.Column(db.String(500), nullable=False)
    analysis_result = db.Column(db.Text, nullable=False)
    timestamp       = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def to_dict(self):
        try:
            parsed = json.loads(self.analysis_result)
        except Exception:
            parsed = self.analysis_result
        return {
            'id':              self.id,
            'user_id':         self.user_id,
            'username':        self.user.name if self.user else 'Unknown',
            'ad_link':         self.ad_link,
            'analysis_result': parsed,
            'timestamp':       self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
