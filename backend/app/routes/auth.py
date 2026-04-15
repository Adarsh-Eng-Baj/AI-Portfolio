"""
routes/auth.py — Authentication endpoints.
Handles admin login, logout, and user profile.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
import bcrypt

from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


# ─────────────────────────────────────────────
# POST /api/auth/login
# ─────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate admin user and return JWT tokens."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Find user by email
    user = User.query.filter_by(email=email, is_active=True).first()
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Verify password with bcrypt
    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Update last login timestamp
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Generate JWT tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


# ─────────────────────────────────────────────
# GET /api/auth/me
# ─────────────────────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Return the currently authenticated user's profile."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200


# ─────────────────────────────────────────────
# POST /api/auth/refresh
# ─────────────────────────────────────────────
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh the access token using a valid refresh token."""
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': new_access_token}), 200


# ─────────────────────────────────────────────
# POST /api/auth/change-password
# ─────────────────────────────────────────────
@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for the authenticated admin user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Both current and new passwords are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400
    
    # Verify current password
    if not bcrypt.checkpw(current_password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Hash and save new password
    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.password_hash = new_hash
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200

# ─────────────────────────────────────────────
# POST /api/auth/reset-password
# ─────────────────────────────────────────────
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset the admin password using a hardcoded recovery PIN."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
        
    email = data.get('email', '').strip().lower()
    recovery_pin = data.get('recovery_pin', '').strip()
    new_password = data.get('new_password', '')
    
    if not email or not recovery_pin or not new_password:
        return jsonify({'error': 'Email, PIN, and new password are required'}), 400
        
    if recovery_pin != "706484":
        return jsonify({'error': 'Invalid recovery PIN'}), 401
        
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
    user = User.query.filter_by(email=email, is_active=True).first()
    if not user:
        return jsonify({'error': 'Admin account not found for this email'}), 404
        
    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.password_hash = new_hash
    db.session.commit()
    
    return jsonify({'message': 'Password successfully reset'}), 200
