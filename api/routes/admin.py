"""
Admin API routes
Handles admin functionality
"""
from flask import Blueprint, jsonify
from api.middleware.auth import login_required, admin_required
from database.models import User, Campaign, CampaignLog

admin_bp = Blueprint('admin', __name__, url_prefix='/api')


@admin_bp.route('/admin/data')
@login_required
@admin_required
def admin_data():
    """Get all system data for admin dashboard"""
    return jsonify({
        'users': [u.to_dict() for u in User.query.all()],
        'campaigns': [c.to_dict() for c in Campaign.query.all()],
        'logs': [l.to_dict() for l in CampaignLog.query.all()]
    }), 200
