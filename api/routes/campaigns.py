"""
Campaigns API routes
Handles campaign management and analytics
"""
import datetime
from flask import Blueprint, jsonify, request, session
from api.middleware.auth import login_required
from database.models import db, Campaign

campaigns_bp = Blueprint('campaigns', __name__, url_prefix='/api')


@campaigns_bp.route('/campaigns', methods=['GET', 'POST'])
@login_required
def campaigns():
    """Get user campaigns or create new campaign"""
    uid = session['user_id']
    
    if request.method == 'GET':
        records = Campaign.query.filter_by(user_id=uid).order_by(Campaign.date.desc()).all()
        return jsonify([r.to_dict() for r in records]), 200
    
    data = request.get_json() or {}
    name = data.get('name', '').strip()
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
    
    c = Campaign(
        user_id=uid,
        name=name,
        platform=platform,
        clicks=int(data.get('clicks', 0)),
        conversions=int(data.get('conversions', 0)),
        spend=float(data.get('spend', 0)),
        revenue=float(data.get('revenue', 0)),
        date=date_val
    )
    db.session.add(c)
    db.session.commit()
    
    return jsonify(c.to_dict()), 201


@campaigns_bp.route('/dashboard')
@login_required
def dashboard():
    """Get dashboard analytics"""
    uid = session['user_id']
    
    r = db.session.query(
        db.func.sum(Campaign.clicks),
        db.func.sum(Campaign.spend),
        db.func.sum(Campaign.revenue),
        db.func.sum(Campaign.conversions)
    ).filter_by(user_id=uid).first()
    
    clicks = r[0] or 0
    spend = r[1] or 0.0
    revenue = r[2] or 0.0
    convs = r[3] or 0
    
    return jsonify({
        'clicks': clicks,
        'impressions': clicks * 30,
        'conversions': convs,
        'revenue': revenue,
        'spend': spend
    }), 200


@campaigns_bp.route('/analyze-performance', methods=['POST'])
@login_required
def analyze_performance():
    """Analyze campaign performance across platforms"""
    uid = session['user_id']
    platforms = ['Instagram', 'Google Ads', 'YouTube']
    stats = {}
    
    for p in platforms:
        r = db.session.query(
            db.func.sum(Campaign.spend),
            db.func.sum(Campaign.revenue)
        ).filter_by(user_id=uid, platform=p).first()
        
        sp = r[0] or 0.0
        rv = r[1] or 0.0
        stats[p] = {
            'spend': sp,
            'revenue': rv,
            'roi': round((rv - sp) / sp * 100 if sp > 0 else 0, 1)
        }
    
    best = max(stats.items(), key=lambda x: x[1]['roi'])
    worst = min(stats.items(), key=lambda x: x[1]['roi'])
    
    analysis = (
        f"Telemetry: {best[0]} yields +{best[1]['roi']}% ROI. "
        f"{worst[0]} underperforms at +{worst[1]['roi']}% ROI. "
        f"Recommend reallocating 20% of {worst[0]} budget to {best[0]}."
    )
    
    return jsonify({'analysis': analysis}), 200
