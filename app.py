import os, re, datetime, json, random
from functools import wraps
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from models import db, User, Post, PostLike, Comment, Message, Connection, Campaign, CampaignLog

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "quantum-antigrav-secret-9000")

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'marketing.db')
db_path = os.path.abspath(db_path).replace('\\', '/')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'webm'}

db.init_app(app)

# ─────────────────────────────────────────────
# DECORATORS
# ─────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'message': 'Unauthenticated'}), 401
            return redirect(url_for('view_login'))
        # Ensure user exists in the database to prevent stale session 500 errors
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            if request.path.startswith('/api/'):
                return jsonify({'message': 'Unauthenticated'}), 401
            return redirect(url_for('view_login'))
        return f(*args, **kwargs)
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('role') != 'Admin':
            return redirect(url_for('view_home'))
        return f(*args, **kwargs)
    return wrap

# ─────────────────────────────────────────────
# MOCK HELPERS
# ─────────────────────────────────────────────
def mock_captions(name):
    n = re.sub(r'[^a-zA-Z0-9 ]', '', name or 'Product').strip().capitalize()
    templates = [
        [f"Defy gravity with {n} — The future is weightless.", f"{n}: Because the ground is just a suggestion.", f"Rise above everything. Rise with {n}."],
        [f"Experience the weightless revolution of {n}.", f"Elevating your perspective — only with {n}.", f"No gravity? No problem. {n} is here."],
        [f"Redefining physics: {n} brings anti-gravity to life.", f"Float higher, dream bigger: Discover {n}.", f"Break the chains of gravity with {n}."],
        [f"Step into the future of motion with {n}.", f"{n} — where gravity becomes optional.", f"Elevate your daily orbit with {n}."]
    ]
    idx = sum(ord(c) for c in n) % len(templates)
    return templates[idx]

def mock_hashtags(kw):
    c = re.sub(r'[^a-zA-Z0-9]', '', kw or 'hover').capitalize()
    tag_options = [
        [f"#{c}Ads", f"#Future{c}", f"#AntiGravity{c}"],
        [f"#{c}Innovation", f"#NextGen{c}", f"#Levitate{c}"],
        [f"#Discover{c}", f"#ZeroGravity{c}", f"#{c}Universe"],
        [f"#{c}Marketing", f"#Smart{c}Campaign", f"#Float{c}"]
    ]
    idx = sum(ord(char) for char in c) % len(tag_options)
    return tag_options[idx]

# ─────────────────────────────────────────────
# ROLE COLORS (used in templates)
# ─────────────────────────────────────────────
ROLE_COLORS = {
    'Influencer':  'purple',
    'AdPublisher': 'cyan',
    'Customer':    'emerald',
    'Admin':       'pink'
}

# ─────────────────────────────────────────────
# FAVICON
# ─────────────────────────────────────────────
@app.route('/favicon.ico')
def favicon():
    return '', 204

# ─────────────────────────────────────────────
# AUTH VIEWS
# ─────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def view_login():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return redirect(url_for('view_home'))
        else:
            session.clear()
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        pwd   = request.form.get('password', '').strip()
        user  = User.query.filter_by(email=email).first()
        if user and user.check_password(pwd):
            session.update({'user_id': user.id, 'username': user.name, 'role': user.role})
            return redirect(url_for('view_admin') if user.role == 'Admin' else url_for('view_home'))
        return render_template('login.html', error='Invalid credentials.')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def view_signup():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return redirect(url_for('view_home'))
        else:
            session.clear()
    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        pwd   = request.form.get('password', '').strip()
        role  = request.form.get('role', 'Customer').strip()
        tagline = request.form.get('tagline', '').strip()
        if not name or not email or not pwd:
            return render_template('signup.html', error='All fields are required.')
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already registered.')
        u = User(name=name, email=email, role=role, tagline=tagline or f'Anti-Gravity {role}')
        u.set_password(pwd)
        db.session.add(u)
        db.session.commit()
        if role == 'Customer':
            _seed_campaigns(u.id)
        session.update({'user_id': u.id, 'username': u.name, 'role': u.role})
        return redirect(url_for('view_admin') if role == 'Admin' else url_for('view_home'))
    return render_template('signup.html')

@app.route('/logout')
def view_logout():
    session.clear()
    return redirect(url_for('view_login'))

# ─────────────────────────────────────────────
# MAIN PAGES
# ─────────────────────────────────────────────
@app.route('/')
@login_required
def view_home():
    if session.get('role') == 'Admin':
        return redirect(url_for('view_admin'))
    user = User.query.get(session['user_id'])
    # unread message count for badge
    unread = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return render_template('home.html', user=user, unread=unread)

@app.route('/feed')
@login_required
def view_feed():
    user = User.query.get(session['user_id'])
    unread = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return render_template('feed.html', user=user, unread=unread)

@app.route('/network')
@login_required
def view_network():
    user = User.query.get(session['user_id'])
    unread = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return render_template('network.html', user=user, unread=unread)

@app.route('/profile/<int:uid>')
@login_required
def view_profile(uid):
    me   = User.query.get(session['user_id'])
    them = User.query.get_or_404(uid)
    unread = Message.query.filter_by(receiver_id=me.id, is_read=False).count()
    # connection status
    conn = Connection.query.filter(
        ((Connection.requester_id == me.id) & (Connection.receiver_id == uid)) |
        ((Connection.requester_id == uid)   & (Connection.receiver_id == me.id))
    ).first()
    conn_status = conn.status if conn else None
    conn_is_mine = conn.requester_id == me.id if conn else False
    return render_template('profile.html', user=me, profile=them, unread=unread,
                           conn_status=conn_status, conn_is_mine=conn_is_mine)

@app.route('/profile/edit')
@login_required
def view_profile_edit():
    user = User.query.get(session['user_id'])
    return render_template('profile_edit.html', user=user)

@app.route('/messages')
@login_required
def view_messages():
    user = User.query.get(session['user_id'])
    return render_template('messages.html', user=user, chat_user=None, chat_user_id=None)

@app.route('/messages/<int:uid>')
@login_required
def view_messages_thread(uid):
    me       = User.query.get(session['user_id'])
    chat_usr = User.query.get_or_404(uid)
    # Mark received messages as read
    Message.query.filter_by(sender_id=uid, receiver_id=me.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('messages.html', user=me, chat_user=chat_usr, chat_user_id=uid)

@app.route('/analytics')
@login_required
def view_analytics():
    user   = User.query.get(session['user_id'])
    unread = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return render_template('analytics.html', user=user, unread=unread)

@app.route('/campaigns')
@login_required
def view_campaigns():
    if session.get('role') == 'Admin':
        return redirect(url_for('view_admin'))
    user   = User.query.get(session['user_id'])
    unread = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return render_template('campaigns.html', username=user.name, unread=unread)

@app.route('/ai')
@login_required
def view_ai():
    if session.get('role') == 'Admin':
        return redirect(url_for('view_admin'))
    user   = User.query.get(session['user_id'])
    unread = Message.query.filter_by(receiver_id=user.id, is_read=False).count()
    return render_template('ai.html', username=user.name, unread=unread)

@app.route('/admin')
@login_required
@admin_required
def view_admin():
    return render_template('admin.html', username=session.get('username'))

# ─────────────────────────────────────────────
# API — PROFILE
# ─────────────────────────────────────────────
@app.route('/api/profile/<int:uid>')
@login_required
def api_profile(uid):
    u = User.query.get_or_404(uid)
    data = u.to_dict()
    data['post_count']     = Post.query.filter_by(user_id=uid).count()
    data['network_count']  = Connection.query.filter(
        ((Connection.requester_id == uid) | (Connection.receiver_id == uid)),
        Connection.status == 'accepted'
    ).count()
    return jsonify(data), 200

@app.route('/api/profile/update', methods=['POST'])
@login_required
def api_profile_update():
    user = User.query.get(session['user_id'])
    data = request.get_json() or {}
    new_name = data.get('name', '').strip()
    if new_name and len(new_name) >= 2:
        user.name = new_name
        session['username'] = new_name
    user.bio        = data.get('bio',        user.bio)
    user.avatar_url = data.get('avatar_url', user.avatar_url)
    user.location   = data.get('location',   user.location)
    user.website    = data.get('website',    user.website)
    user.tagline    = data.get('tagline',    user.tagline)
    db.session.commit()
    return jsonify(user.to_dict()), 200

@app.route('/api/profile/delete', methods=['POST'])
@login_required
def api_profile_delete():
    user = User.query.get(session['user_id'])
    db.session.delete(user)
    db.session.commit()
    session.clear()
    return jsonify({'message': 'Account deleted successfully'}), 200

@app.route('/api/upload', methods=['POST'])
@login_required
def api_upload():
    """Accept multipart image upload, save to static/uploads/, return public URL."""
    if 'file' not in request.files:
        return jsonify({'message': 'No file in request'}), 400
    f = request.files['file']
    if not f or f.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({'message': f'File type .{ext} not allowed'}), 400
    uid      = session['user_id']
    ts       = int(datetime.datetime.utcnow().timestamp())
    filename = secure_filename(f"{uid}_{ts}.{ext}")
    f.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({'url': f'/static/uploads/{filename}'}), 200


# ─────────────────────────────────────────────
# API — FEED / POSTS
# ─────────────────────────────────────────────
@app.route('/api/posts', methods=['GET', 'POST'])
@login_required
def api_posts():
    if request.method == 'GET':
        posts = Post.query.order_by(Post.timestamp.desc()).limit(50).all()
        return jsonify([p.to_dict() for p in posts]), 200
    data      = request.get_json() or {}
    content   = data.get('content', '').strip()
    image_url = data.get('image_url', '').strip()
    reel_url  = data.get('reel_url', '').strip()
    if not content and not image_url and not reel_url:
        return jsonify({'message': 'Content is required'}), 400
    p = Post(user_id=session['user_id'],
             content=content or '📸',
             image_url=image_url or None,
             reel_url=reel_url or None)
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
@login_required
def api_post_like(post_id):
    p   = Post.query.get_or_404(post_id)
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


@app.route('/api/posts/<int:post_id>/comments', methods=['GET', 'POST'])
@login_required
def api_post_comments(post_id):
    Post.query.get_or_404(post_id)  # ensure post exists
    if request.method == 'GET':
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.timestamp.asc()).all()
        return jsonify([c.to_dict() for c in comments]), 200
    data    = request.get_json() or {}
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'message': 'Comment cannot be empty'}), 400
    c = Comment(post_id=post_id, user_id=session['user_id'], content=content)
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201


@app.route('/api/posts/<int:post_id>/liked', methods=['GET'])
@login_required
def api_post_liked(post_id):
    uid = session['user_id']
    liked = PostLike.query.filter_by(post_id=post_id, user_id=uid).first() is not None
    return jsonify({'liked': liked}), 200

# ─────────────────────────────────────────────
# API — NETWORK
# ─────────────────────────────────────────────
@app.route('/api/network')
@login_required
def api_network():
    me       = session['user_id']
    role_filter = request.args.get('role')
    q = User.query.filter(User.id != me, User.role != 'Admin')
    if role_filter:
        q = q.filter_by(role=role_filter)
    users = q.all()

    result = []
    for u in users:
        d = u.to_dict()
        # connection status between me and this user
        conn = Connection.query.filter(
            ((Connection.requester_id == me) & (Connection.receiver_id == u.id)) |
            ((Connection.requester_id == u.id) & (Connection.receiver_id == me))
        ).first()
        d['conn_status']  = conn.status if conn else None
        d['conn_is_mine'] = (conn.requester_id == me) if conn else False
        d['post_count']   = Post.query.filter_by(user_id=u.id).count()
        result.append(d)
    return jsonify(result), 200

# ─────────────────────────────────────────────
# API — CONNECTIONS
# ─────────────────────────────────────────────
@app.route('/api/connect/<int:uid>', methods=['POST'])
@login_required
def api_connect(uid):
    me = session['user_id']
    if me == uid:
        return jsonify({'message': 'Cannot connect to yourself'}), 400

    data   = request.get_json() or {}
    action = data.get('action', 'request')   # request | accept | cancel

    conn = Connection.query.filter(
        ((Connection.requester_id == me)  & (Connection.receiver_id == uid)) |
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

# ─────────────────────────────────────────────
# API — MESSAGES
# ─────────────────────────────────────────────
@app.route('/api/messages/inbox')
@login_required
def api_inbox():
    me = session['user_id']
    # All users I have exchanged at least one message with
    sent_ids = db.session.query(Message.receiver_id).filter_by(sender_id=me).distinct()
    recv_ids = db.session.query(Message.sender_id).filter_by(receiver_id=me).distinct()
    partner_ids = set([r[0] for r in sent_ids] + [r[0] for r in recv_ids])

    inbox = []
    for pid in partner_ids:
        partner = User.query.get(pid)
        if not partner:
            continue
        last_msg = Message.query.filter(
            ((Message.sender_id == me)   & (Message.receiver_id == pid)) |
            ((Message.sender_id == pid)  & (Message.receiver_id == me))
        ).order_by(Message.timestamp.desc()).first()
        unread_count = Message.query.filter_by(sender_id=pid, receiver_id=me, is_read=False).count()
        inbox.append({
            'partner_id':    partner.id,
            'partner_name':  partner.name,
            'partner_role':  partner.role,
            'partner_avatar': partner.avatar_url or '',
            'last_message':  last_msg.content[:60] if last_msg else '',
            'last_ts':       last_msg.timestamp.strftime('%H:%M') if last_msg else '',
            'unread':        unread_count
        })
    # Sort by last message time
    inbox.sort(key=lambda x: x['last_ts'], reverse=True)
    return jsonify(inbox), 200

@app.route('/api/messages/<int:uid>', methods=['GET', 'POST'])
@login_required
def api_messages_thread(uid):
    me = session['user_id']
    if request.method == 'GET':
        msgs = Message.query.filter(
            ((Message.sender_id == me)   & (Message.receiver_id == uid)) |
            ((Message.sender_id == uid)  & (Message.receiver_id == me))
        ).order_by(Message.timestamp.asc()).all()
        # Mark as read
        Message.query.filter_by(sender_id=uid, receiver_id=me, is_read=False).update({'is_read': True})
        db.session.commit()
        return jsonify([m.to_dict() for m in msgs]), 200

    data    = request.get_json() or {}
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'message': 'Empty message'}), 400
    m = Message(sender_id=me, receiver_id=uid, content=content)
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201

@app.route('/api/messages/unread-count')
@login_required
def api_unread_count():
    count = Message.query.filter_by(receiver_id=session['user_id'], is_read=False).count()
    return jsonify({'count': count}), 200

# ─────────────────────────────────────────────
# API — CAMPAIGNS (user-scoped)
# ─────────────────────────────────────────────
@app.route('/api/campaigns', methods=['GET', 'POST'])
@login_required
def api_campaigns():
    uid = session['user_id']
    if request.method == 'GET':
        records = Campaign.query.filter_by(user_id=uid).order_by(Campaign.date.desc()).all()
        return jsonify([r.to_dict() for r in records]), 200
    data = request.get_json() or {}
    name     = data.get('name', '').strip()
    platform = data.get('platform', '')
    date_str = data.get('date', '')
    if not name:
        return jsonify({'message': 'Campaign Name required'}), 400
    if platform not in ['Instagram', 'Google Ads', 'YouTube']:
        return jsonify({'message': 'Invalid platform'}), 400
    try:
        date_val = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date'}), 400
    c = Campaign(user_id=uid, name=name, platform=platform,
                 clicks=int(data.get('clicks', 0)),
                 conversions=int(data.get('conversions', 0)),
                 spend=float(data.get('spend', 0)),
                 revenue=float(data.get('revenue', 0)),
                 date=date_val)
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201

# ─────────────────────────────────────────────
# API — ANALYTICS DASHBOARD
# ─────────────────────────────────────────────
@app.route('/api/dashboard')
@login_required
def api_dashboard():
    uid = session['user_id']
    r = db.session.query(
        db.func.sum(Campaign.clicks),
        db.func.sum(Campaign.spend),
        db.func.sum(Campaign.revenue),
        db.func.sum(Campaign.conversions)
    ).filter_by(user_id=uid).first()
    clicks = r[0] or 0; spend = r[1] or 0.0; revenue = r[2] or 0.0; convs = r[3] or 0
    return jsonify({'clicks': clicks, 'impressions': clicks*30,
                    'conversions': convs, 'revenue': revenue, 'spend': spend}), 200

@app.route('/api/analyze-performance', methods=['POST'])
@login_required
def api_analyze_performance():
    uid = session['user_id']
    platforms = ['Instagram', 'Google Ads', 'YouTube']
    stats = {}
    for p in platforms:
        r = db.session.query(db.func.sum(Campaign.spend), db.func.sum(Campaign.revenue)).filter_by(user_id=uid, platform=p).first()
        sp = r[0] or 0.0; rv = r[1] or 0.0
        stats[p] = {'spend': sp, 'revenue': rv, 'roi': round((rv-sp)/sp*100 if sp > 0 else 0, 1)}
    best  = max(stats.items(), key=lambda x: x[1]['roi'])
    worst = min(stats.items(), key=lambda x: x[1]['roi'])
    analysis = (f"Telemetry: {best[0]} yields +{best[1]['roi']}% ROI. "
                f"{worst[0]} underperforms at +{worst[1]['roi']}% ROI. "
                f"Recommend reallocating 20% of {worst[0]} budget to {best[0]}.")
    return jsonify({'analysis': analysis}), 200

# ─────────────────────────────────────────────
# API — AI WORKSPACE (OLLAMA INTEGRATION)
# ─────────────────────────────────────────────
import requests

def extract_keywords_from_url(url):
    """
    Extracts meaningful keywords from an ad URL (like product name, promo, deals).
    """
    if not url:
        return []
    # Strip protocol and domain parts
    clean_url = re.sub(r'https?://(?:www\.)?', '', url.lower())
    # Find all alphabetical chunks of length >= 3
    words = re.findall(r'[a-z]{3,}', clean_url)
    # Ignore common url/domain terms
    ignore = {
        'com', 'org', 'net', 'www', 'http', 'https', 'html', 'php', 'watch', 'watchv', 
        'utm', 'source', 'medium', 'campaign', 'link', 'ads', 'adlink', 'instagram', 
        'youtube', 'facebook', 'tiktok', 'google', 'twitter', 'linkedin', 'pinterest'
    }
    filtered = [w for w in words if w not in ignore]
    # Remove duplicates but keep order
    seen = set()
    return [w for w in filtered if not (w in seen or seen.add(w))]

def clean_json_response(text):
    """
    Cleans Ollama output from markdown and formatting to parse it as raw JSON.
    """
    if not text:
        return None
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
        
    try:
        return json.loads(text)
    except Exception:
        # Simple cleanup helper for trailing commas and formatting
        try:
            cleaned = re.sub(r',\s*([\]}])', r'\1', text) # trailing commas
            cleaned = cleaned.replace("'", '"') # single to double quotes
            return json.loads(cleaned)
        except Exception:
            return None

def query_ollama(prompt, json_mode=False):
    """
    Sends a query to local Ollama API.
    Checks available models and uses the first available one, defaulting to 'qwen2.5:0.5b'.
    """
    ollama_url = "http://localhost:11434/api"
    try:
        # Check list of models
        resp = requests.get(f"{ollama_url}/tags", timeout=2)
        models = []
        if resp.status_code == 200:
            models = [m['name'] for m in resp.json().get('models', [])]
        
        # Determine model to use
        model = 'qwen2.5:0.5b'
        if models:
            # If our preferred model or its variations are in the list, use it
            preferred = ['qwen2.5:0.5b', 'tinyllama', 'llama3.2:1b']
            for p in preferred:
                if any(p in m for m in models):
                    model = next(m for m in models if p in m)
                    break
            else:
                model = models[0] # Fallback to first available model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if json_mode:
            payload["format"] = "json"
            
        res = requests.post(f"{ollama_url}/generate", json=payload, timeout=40)
        if res.status_code == 200:
            content = res.json().get('response', '')
            return content
    except Exception as e:
        print(f"Ollama query failed: {e}")
    return None

CHAT_HISTORIES = {}

def query_ollama_chat(messages):
    """
    Sends a chat conversation history to the local Ollama chat API.
    Checks available models and uses the first available one, defaulting to 'qwen2.5:0.5b'.
    Enhanced for detailed, comprehensive responses.
    """
    ollama_url = "http://localhost:11434/api"
    try:
        # Check list of models
        resp = requests.get(f"{ollama_url}/tags", timeout=2)
        models = []
        if resp.status_code == 200:
            models = [m['name'] for m in resp.json().get('models', [])]
        
        # Determine model to use
        model = 'qwen2.5:0.5b'
        if models:
            preferred = ['qwen2.5:0.5b', 'tinyllama', 'llama3.2:1b', 'llama3.2:3b']
            for p in preferred:
                if any(p in m for m in models):
                    model = next(m for m in models if p in m)
                    break
            else:
                model = models[0] # Fallback to first available model
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 2048  # Allow longer responses
            }
        }
        res = requests.post(f"{ollama_url}/chat", json=payload, timeout=90)
        if res.status_code == 200:
            content = res.json().get('message', {}).get('content', '')
            return content
    except Exception as e:
        print(f"Ollama chat query failed: {e}")
    return None

@app.route('/api/generate-caption', methods=['POST'])
@login_required
def api_generate_caption():
    data = request.get_json() or {}
    name = data.get('productName', '').strip()
    if not name:
        return jsonify({'message': 'productName required'}), 400

    # 1. Try local Ollama first
    prompt = f"Generate 3 anti-gravity marketing slogans for the product: {name}. Return a JSON object with a single key 'captions' containing a list of 3 strings. Example: {{\"captions\": [\"Slogan 1\", \"Slogan 2\", \"Slogan 3\"]}}"
    ollama_resp = query_ollama(prompt, json_mode=True)
    if ollama_resp:
        cleaned_json = clean_json_response(ollama_resp)
        if cleaned_json and 'captions' in cleaned_json and isinstance(cleaned_json['captions'], list):
            # Normalize captions elements to strings
            caps = []
            for item in cleaned_json['captions']:
                if isinstance(item, dict):
                    val = item.get('content') or item.get('value') or item.get('slogan') or item.get('text') or str(item)
                    caps.append(val)
                elif isinstance(item, str):
                    caps.append(item)
            if caps:
                return jsonify({'captions': caps[:3], 'isMock': False, 'ai_source': 'Ollama'}), 200

    # 2. Fall back to OpenAI
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if api_key and api_key != 'your_openai_api_key_here':
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{'role':'system','content':'Generate 3 anti-gravity marketing slogans. Return JSON {captions:[...]}'},
                          {'role':'user','content':f'Product: {name}'}],
                response_format={'type':'json_object'})
            result = json.loads(resp.choices[0].message.content)
            return jsonify({'captions': result.get('captions',[])[:3], 'isMock': False, 'ai_source': 'OpenAI'}), 200
        except Exception:
            pass

    # 3. Fall back to mock helper
    return jsonify({'captions': mock_captions(name), 'isMock': True}), 200

@app.route('/api/generate-hashtags', methods=['POST'])
@login_required
def api_generate_hashtags():
    data = request.get_json() or {}
    kw   = data.get('keyword', '').strip()
    if not kw:
        return jsonify({'message': 'keyword required'}), 400

    # 1. Try local Ollama first
    prompt = f"Generate 3 trending social media hashtags for the keyword: {kw}. Return a JSON object with a single key 'hashtags' containing a list of 3 strings (each starting with '#'). Example: {{\"hashtags\": [\"#Tag1\", \"#Tag2\", \"#Tag3\"]}}"
    ollama_resp = query_ollama(prompt, json_mode=True)
    if ollama_resp:
        cleaned_json = clean_json_response(ollama_resp)
        if cleaned_json and 'hashtags' in cleaned_json and isinstance(cleaned_json['hashtags'], list):
            tags = []
            for item in cleaned_json['hashtags']:
                if isinstance(item, dict):
                    val = item.get('tag') or item.get('name') or item.get('value') or item.get('text') or str(item)
                    tags.append(val)
                elif isinstance(item, str):
                    tags.append(item)
            cleaned_tags = [t if t.startswith('#') else f'#{t}' for t in tags]
            if cleaned_tags:
                return jsonify({'hashtags': cleaned_tags[:3], 'isMock': False, 'ai_source': 'Ollama'}), 200

    # 2. Fall back to OpenAI
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if api_key and api_key != 'your_openai_api_key_here':
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{'role':'system','content':'Generate 3 trending hashtags. Return JSON {hashtags:[...]}'},
                          {'role':'user','content':f'Keyword: {kw}'}],
                response_format={'type':'json_object'})
            result = json.loads(resp.choices[0].message.content)
            return jsonify({'hashtags': result.get('hashtags',[])[:3], 'isMock': False, 'ai_source': 'OpenAI'}), 200
        except Exception:
            pass

    # 3. Fall back to mock helper
    return jsonify({'hashtags': mock_hashtags(kw), 'isMock': True}), 200

@app.route('/api/analyze-link', methods=['POST'])
@login_required
def api_analyze_link():
    data    = request.get_json() or {}
    ad_link = data.get('adLink', '').strip()
    if not ad_link:
        return jsonify({'message': 'adLink required'}), 400
    uid     = session['user_id']
    
    # Defaults and fallback metrics
    ctr     = round(random.uniform(2.1, 7.8), 2)
    clicks  = random.randint(800, 2500)
    convs   = int(clicks * random.uniform(0.02, 0.07))
    spend   = round(random.uniform(300, 950), 2)
    revenue = round(spend * random.uniform(1.8, 4.5), 2)
    eng     = round(random.uniform(5.5, 18.2), 2)
    
    # Parse platform and keywords
    platform = 'Instagram' if 'instagram' in ad_link.lower() else ('YouTube' if 'youtube' in ad_link.lower() else 'Google Ads')
    if 'facebook' in ad_link.lower():
        platform = 'Facebook'
    elif 'tiktok' in ad_link.lower():
        platform = 'TikTok'
        
    keywords = extract_keywords_from_url(ad_link)
    keywords_str = ", ".join(keywords) if keywords else "general marketing"
    
    # Defaults for tags and verdict
    if keywords:
        hashtags = [f"#{k.capitalize()}" for k in keywords[:2]]
        hashtags.append(f"#{platform.replace(' ', '')}Campaign")
        product_title = " ".join([k.capitalize() for k in keywords])
        verdict = f"Targeted {platform} campaign focusing on '{product_title}'. Landing page optimized to convert search intent with relevant copy."
    else:
        hashtags = mock_hashtags(platform)
        verdict  = f"High-velocity {platform} campaign detected. Clean landing page layout and clear call to action."
        
    ai_source = 'Mock'

    # 1. Try local Ollama first
    prompt = (
        f"Analyze this marketing ad URL: '{ad_link}'.\n"
        f"Context keywords extracted from URL: {keywords_str}.\n"
        f"Identify the platform (Instagram, Google Ads, YouTube, TikTok, Facebook) and write a detailed marketing analysis verdict "
        f"about the target product/keywords ({keywords_str}) and campaign strategy (max 2 sentences).\n"
        f"Return a JSON object with the keys 'platform' (string), 'hashtags' (list of 3 strings), and 'verdict' (string). "
        f"Example: {{\"platform\": \"YouTube\", \"hashtags\": [\"#Review\", \"#Tech\", \"#Viral\"], \"verdict\": \"YouTube campaign driving traffic for the target product using video engagement.\"}}"
    )
    ollama_resp = query_ollama(prompt, json_mode=True)
    if ollama_resp:
        cleaned_json = clean_json_response(ollama_resp)
        if cleaned_json:
            if 'platform' in cleaned_json:
                platform = cleaned_json['platform']
            if 'hashtags' in cleaned_json and isinstance(cleaned_json['hashtags'], list):
                tags = []
                for item in cleaned_json['hashtags']:
                    if isinstance(item, dict):
                        val = item.get('tag') or item.get('name') or item.get('value') or item.get('text') or str(item)
                        tags.append(val)
                    elif isinstance(item, str):
                        tags.append(item)
                hashtags = [t if t.startswith('#') else f'#{t}' for t in tags]
            if 'verdict' in cleaned_json:
                verdict = cleaned_json['verdict']
            ai_source = 'Ollama'

    insights = {
        'predicted_ctr': f'{ctr}%', 
        'estimated_engagement': f'{eng}%',
        'hashtags': hashtags[:3],
        'verdict': verdict,
        'ai_source': ai_source
    }
    
    log = CampaignLog(user_id=uid, ad_link=ad_link, analysis_result=json.dumps(insights))
    db.session.add(log)
    
    match = re.search(r'https?://(?:www\.)?([^/.]+)', ad_link)
    cname = f"Audit: {match.group(1).capitalize()}" if match else f"{platform} Ad Audit"
    camp = Campaign(user_id=uid, name=cname, platform=platform[:50], clicks=clicks,
                    conversions=convs, spend=spend, revenue=revenue, date=datetime.date.today())
    db.session.add(camp)
    db.session.commit()
    
    return jsonify({'log': log.to_dict(), 'campaign': camp.to_dict()}), 201

@app.route('/api/campaign-logs')
@login_required
def api_campaign_logs():
    logs = CampaignLog.query.filter_by(user_id=session['user_id']).order_by(CampaignLog.timestamp.desc()).all()
    return jsonify([l.to_dict() for l in logs]), 200

@app.route('/api/ai-chat', methods=['POST'])
@login_required
def api_ai_chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'message': 'message required'}), 400
        
    uid = session['user_id']
    user = User.query.get(uid)
    campaigns = Campaign.query.filter_by(user_id=uid).all()
    logs = CampaignLog.query.filter_by(user_id=uid).all()
    
    # Initialize history list
    if uid not in CHAT_HISTORIES:
        CHAT_HISTORIES[uid] = []
        
    # Append user message
    CHAT_HISTORIES[uid].append({"role": "user", "content": message})
    # Keep only last 10 messages to prevent memory blow-out
    CHAT_HISTORIES[uid] = CHAT_HISTORIES[uid][-10:]
    
    # Check if user query is asking about database metrics/campaigns
    query_lower = message.lower()
    campaign_keywords = {
        "campaign", "my ad", "performance", "roi", "clicks", "conversion", "spend", 
        "revenue", "metrics", "history", "log", "analytics", "stats", "telemetry", 
        "audit", "scraped", "database", "record"
    }
    campaign_names = [c.name.lower() for c in campaigns]
    has_campaign_name_match = any(name in query_lower for name in campaign_names)
    is_asking_about_db = any(kw in query_lower for kw in campaign_keywords) or has_campaign_name_match
    
    # Compile database context ONLY if user query is database/campaign related
    context_parts = []
    if is_asking_about_db:
        if user:
            context_parts.append(f"User Profile: Name: {user.name}, Email: {user.email}, Role: {user.role}, Tagline: {user.tagline or 'N/A'}")
            
        if campaigns:
            context_parts.append("Active Campaigns:")
            for c in campaigns:
                roi = ((c.revenue - c.spend) / c.spend * 100) if c.spend > 0 else 0
                context_parts.append(
                    f"- Campaign Name: '{c.name}' on Platform: {c.platform} | Clicks: {c.clicks}, Conversions: {c.conversions}, "
                    f"Spend: ${c.spend:.2f}, Revenue: ${c.revenue:.2f}, ROI: {roi:.1f}%"
                )
                
        if logs:
            context_parts.append("Recent URL Audit Logs:")
            for l in logs:
                try:
                    insights = json.loads(l.analysis_result)
                except:
                    insights = {}
                verdict = insights.get('verdict', 'N/A')
                context_parts.append(f"- Audited adLink: '{l.ad_link}' | Verdict: {verdict}")
                
    context_str = "\n".join(context_parts) if context_parts else ""
    
    # Form message payload for chat format models
    if context_str:
        system_content = (
            f"You are an expert AI marketing assistant with comprehensive knowledge in digital marketing, advertising, and campaign optimization.\n\n"
            f"USER DATABASE CONTEXT:\n"
            f"=========================================\n"
            f"{context_str}\n"
            f"=========================================\n\n"
            f"RESPONSE GUIDELINES:\n"
            f"1. Provide COMPREHENSIVE and DETAILED answers (minimum 4-6 paragraphs for general queries)\n"
            f"2. Structure your response with clear sections and formatting:\n"
            f"   - Use **bold** for important terms, headers, and key points\n"
            f"   - Use bullet points (•) for lists and features\n"
            f"   - Use numbered lists (1., 2., 3.) for steps or sequences\n"
            f"   - Add line breaks between sections for better readability\n"
            f"3. When answering queries about products, services, businesses, or locations:\n"
            f"   - Provide specific, actionable information\n"
            f"   - Include relevant details like contact info, addresses, hours if applicable to the topic\n"
            f"   - Organize information in clearly labeled sections\n"
            f"   - Use emojis strategically (📍 locations, 📞 contact, ⏰ hours, 🌐 websites, 📊 stats)\n"
            f"4. Reference the user's campaign data and metrics when relevant\n"
            f"5. Provide actionable insights, specific recommendations, and detailed explanations\n"
            f"6. If you don't have specific factual information, provide comprehensive general guidance and best practices\n\n"
            f"Answer the user's query with rich detail and structure:"
        )
    else:
        system_content = (
            f"You are an expert AI marketing assistant with comprehensive knowledge across all aspects of digital marketing.\n\n"
            f"RESPONSE GUIDELINES:\n"
            f"1. Provide COMPREHENSIVE and DETAILED answers (minimum 4-6 paragraphs)\n"
            f"2. Structure responses clearly:\n"
            f"   - Use **bold** for important terms and section headers\n"
            f"   - Use bullet points (•) for lists\n"
            f"   - Use numbered lists for steps/sequences\n"
            f"   - Add line breaks between sections\n"
            f"3. When asked about specific topics (products, companies, marketing strategies):\n"
            f"   - Provide in-depth explanations\n"
            f"   - Include multiple aspects and perspectives\n"
            f"   - Give practical, actionable advice\n"
            f"   - Use examples where helpful\n"
            f"4. Format responses for easy reading with clear visual structure\n"
            f"5. Use emojis strategically for visual markers\n\n"
            f"User Query: {message}\n\n"
            f"Provide a comprehensive, well-structured response:"
        )
    
    messages_payload = [{"role": "system", "content": system_content}]
    messages_payload.extend(CHAT_HISTORIES[uid])
    
    # 1. Try local Ollama chat first
    ollama_resp = query_ollama_chat(messages_payload)
    if ollama_resp:
        response_text = ollama_resp.strip()
        CHAT_HISTORIES[uid].append({"role": "assistant", "content": response_text})
        return jsonify({'response': response_text, 'isMock': False, 'ai_source': 'Ollama'}), 200
        
    # 2. OpenAI Fallback
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if api_key and api_key != 'your_openai_api_key_here':
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=messages_payload
            )
            response_text = resp.choices[0].message.content.strip()
            CHAT_HISTORIES[uid].append({"role": "assistant", "content": response_text})
            return jsonify({'response': response_text, 'isMock': False, 'ai_source': 'OpenAI'}), 200
        except Exception:
            pass
            
    # 3. Mock fallback
    if is_asking_about_db:
        if campaigns:
            c = campaigns[-1]
            roi = ((c.revenue - c.spend) / c.spend * 100) if c.spend > 0 else 0
            response_text = f"Based on your database record, your campaign '{c.name}' on {c.platform} is currently running with {c.clicks} clicks, {c.conversions} conversions, and a spend of ${c.spend:.2f}. The ROI is currently {roi:.1f}%."
            CHAT_HISTORIES[uid].append({"role": "assistant", "content": response_text})
            return jsonify({
                'response': response_text,
                'isMock': True,
                'ai_source': 'Mock'
            }), 200
            
    mock_responses = [
        "To optimize your marketing strategy, consider conducting A/B testing on your headlines and targeting high-intent long-tail keywords.",
        "A great Instagram strategy involves engaging visuals, storytelling in captions, and 3-5 hyper-relevant hashtags to build organic reach.",
        "To boost conversion rates, simplify your landing page checkout funnel, add clear trust badges, and present a compelling call-to-action.",
        f"Focusing on the customer's primary pain point in your copy is usually the fastest way to drive engagement for your brand."
    ]
    idx = sum(ord(c) for c in message) % len(mock_responses)
    response_text = mock_responses[idx]
    CHAT_HISTORIES[uid].append({"role": "assistant", "content": response_text})
    return jsonify({'response': response_text, 'isMock': True}), 200

@app.route('/api/ai-chat/clear', methods=['POST'])
@login_required
def api_ai_chat_clear():
    uid = session['user_id']
    if uid in CHAT_HISTORIES:
        CHAT_HISTORIES[uid] = []
    return jsonify({'message': 'Chat history cleared successfully'}), 200

# ─────────────────────────────────────────────
# API — ADMIN
# ─────────────────────────────────────────────
@app.route('/api/admin/data')
@login_required
@admin_required
def api_admin_data():
    return jsonify({
        'users':     [u.to_dict() for u in User.query.all()],
        'campaigns': [c.to_dict() for c in Campaign.query.all()],
        'logs':      [l.to_dict() for l in CampaignLog.query.all()]
    }), 200

# ─────────────────────────────────────────────
# SEEDING
# ─────────────────────────────────────────────
def _seed_campaigns(uid):
    samples = [
        Campaign(user_id=uid, name='Levitation Boots Launch',  platform='Instagram',  clicks=1250, conversions=85,  spend=750,  revenue=4250,  date=datetime.date(2026,6,10)),
        Campaign(user_id=uid, name='Zero-G Board Display',     platform='Google Ads', clicks=3100, conversions=210, spend=2150, revenue=10500, date=datetime.date(2026,6,15)),
        Campaign(user_id=uid, name='Hover Scooter Vlog',       platform='YouTube',    clicks=4500, conversions=180, spend=3000, revenue=15000, date=datetime.date(2026,6,20)),
        Campaign(user_id=uid, name='Anti-Grav Cushion Promos', platform='Instagram',  clicks=1900, conversions=140, spend=1100, revenue=7000,  date=datetime.date(2026,6,25)),
        Campaign(user_id=uid, name='Hoverboard Search Leads',  platform='Google Ads', clicks=2800, conversions=190, spend=1800, revenue=9500,  date=datetime.date(2026,7,1)),
        Campaign(user_id=uid, name='Space Boots Assembly',     platform='YouTube',    clicks=5200, conversions=230, spend=3500, revenue=19500, date=datetime.date(2026,7,3)),
    ]
    db.session.bulk_save_objects(samples)
    db.session.commit()

def _seed_system():
    if User.query.count() > 0:
        return
    print("Seeding system with default accounts...")
    accounts = [
        ('Commander Admin',     'admin@antigravity.io',      'adminpassword',  'Admin',       'System Administrator'),
        ('Alex Drift',          'influencer@antigravity.io', 'pass123',        'Influencer',  'Anti-Gravity Content Creator & Hover Tech Reviewer'),
        ('Nova Ads Corp',       'adpub@antigravity.io',      'pass123',        'AdPublisher', 'Premium Ad Slots for Hover & Zero-G Products'),
        ('Jordan Customer',     'customer@antigravity.io',   'pass123',        'Customer',    'Zero-G Enthusiast & Early Adopter'),
    ]
    avatars = [
        'https://i.pravatar.cc/150?img=5',
        'https://i.pravatar.cc/150?img=12',
        'https://i.pravatar.cc/150?img=25',
        'https://i.pravatar.cc/150?img=47',
    ]
    bios = [
        'Overseeing all marketing operations in the Anti-Gravity universe.',
        'Creating viral content for hover shoes, levitation boards, and zero-g experiences. DMs open for brand collabs!',
        'We help brands reach the anti-gravity audience. Competitive rates, premium slots across Instagram, Google & YouTube.',
        'Early adopter of all things anti-gravity. Always looking for the next big launch to invest in.',
    ]
    created = []
    for (name, email, pwd, role, tagline), avatar, bio in zip(accounts, avatars, bios):
        u = User(name=name, email=email, role=role, tagline=tagline, avatar_url=avatar, bio=bio, location='New Orbit City')
        u.set_password(pwd)
        db.session.add(u)
        db.session.flush()
        created.append(u)

    db.session.commit()

    # Seed campaigns for Customer
    customer = next(u for u in created if u.role == 'Customer')
    _seed_campaigns(customer.id)

    # Seed some posts
    influencer = next(u for u in created if u.role == 'Influencer')
    adpub      = next(u for u in created if u.role == 'AdPublisher')
    post_data = [
        (influencer.id, "🚀 Just tested the new Hover Boots X9 — absolutely mind-blowing! Zero-G activation in 3 seconds flat. #HoverTech #AntiGravity"),
        (influencer.id, "✨ My latest Zero-G Board review is live! Reach out if your brand wants a feature. DMs open for brand partnerships!"),
        (adpub.id,      "📢 New ad slots available for Q3 2026! Premium placements on Instagram Reels and YouTube Shorts for hover-tech brands. Inquire now."),
        (adpub.id,      "💡 Did you know? Anti-Gravity product ads get 3.2× higher CTR than traditional gadget ads. Get featured in our network!"),
        (customer.id,   "🛒 Just placed an order for the Levitation Boots. Fingers crossed they ship before the weekend! #AntiGravity"),
    ]
    for uid, content in post_data:
        db.session.add(Post(user_id=uid, content=content))

    # Seed a sample message conversation
    db.session.add(Message(sender_id=customer.id, receiver_id=influencer.id,
                           content="Hi Alex! Huge fan of your hover content. Would love to collab on a Zero-G Board review. Interested?"))
    db.session.add(Message(sender_id=influencer.id, receiver_id=customer.id,
                           content="Hey! Thanks so much 🙌 Absolutely open to it. Send me the product details and we can discuss rates!"))

    # Seed a connection
    db.session.add(Connection(requester_id=customer.id, receiver_id=influencer.id, status='accepted'))
    db.session.commit()
    print("Seeding complete.")

with app.app_context():
    db.create_all()
    _seed_system()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
