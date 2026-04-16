from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Setting, User
from app import db

settings_bp = Blueprint('settings', __name__)

# ── Public Endpoints ────────────────────────────────────

@settings_bp.route('/public', methods=['GET'])
def get_public_settings():
    """Returns only public-safe settings (e.g. maintenance_mode)."""
    settings = Setting.query.all()
    public_keys = ['maintenance_mode'] # Add more keys here if they are safe to show publicly
    
    data = {}
    for s in settings:
        if s.key in public_keys:
            # Convert 'true'/'false' strings to boolean for easier JS handling
            val = s.value
            if val.lower() == 'true': val = True
            elif val.lower() == 'false': val = False
            data[s.key] = val
            
    return jsonify(data), 200


# ── Protected Endpoints (Admin Only) ───────────────────

@settings_bp.route('', methods=['GET'])
@jwt_required()
def list_settings():
    """Returns all settings with descriptions."""
    # Check if user is admin
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    settings = Setting.query.all()
    return jsonify([s.to_dict() for s in settings]), 200


@settings_bp.route('/<key>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_setting(key):
    """Updates a specific setting value."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    setting = Setting.query.filter_by(key=key).first()
    if not setting:
        return jsonify({'error': 'Setting not found'}), 404

    data = request.get_json()
    if 'value' not in data:
        return jsonify({'error': 'Value is required'}), 400

    # Convert true/false booleans from JSON to strings if necessary
    val = data['value']
    if isinstance(val, bool):
        val = str(val).lower()
    
    setting.value = str(val)
    db.session.commit()

    return jsonify(setting.to_dict()), 200
