"""
routes/experience.py — Education and work history endpoints.
Public reads, JWT-protected writes.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models import Experience

experience_bp = Blueprint('experience', __name__)


# ─────────────────────────────────────────────
# GET /api/experience
# ─────────────────────────────────────────────
@experience_bp.route('', methods=['GET'])
def get_experience():
    """List all education and work items."""
    exp_type = request.args.get('type')
    
    query = Experience.query
    if exp_type:
        query = query.filter(Experience.type == exp_type)
        
    experiences = query.order_by(Experience.order_index.asc(), Experience.start_date.desc()).all()
    
    return jsonify({
        'experience': [e.to_dict() for e in experiences],
        'total': len(experiences)
    }), 200


# ─────────────────────────────────────────────
# POST /api/experience
# ─────────────────────────────────────────────
@experience_bp.route('', methods=['POST'])
@jwt_required()
def create_experience():
    """Add a new experience/education item (admin only)."""
    data = request.get_json()
    
    if not data or 'role' not in data:
        return jsonify({'error': 'Role/Degree is required'}), 400
        
    exp = Experience(
        type=data.get('type', 'education'),
        company=data.get('company', ''),
        role=data['role'].strip(),
        location=data.get('location', ''),
        start_date=data.get('start_date', ''),
        end_date=data.get('end_date', ''),
        description=data.get('description', ''),
        is_current=data.get('is_current', False),
        order_index=data.get('order_index', 0)
    )
    
    db.session.add(exp)
    db.session.commit()
    
    return jsonify({'message': 'Experience added', 'experience': exp.to_dict()}), 201


# ─────────────────────────────────────────────
# PUT /api/experience/<id>
# ─────────────────────────────────────────────
@experience_bp.route('/<int:exp_id>', methods=['PUT'])
@jwt_required()
def update_experience(exp_id):
    """Update an experience item (admin only)."""
    exp = Experience.query.get_or_404(exp_id)
    data = request.get_json() or {}
    
    if 'type' in data: exp.type = data['type']
    if 'company' in data: exp.company = data['company']
    if 'role' in data: exp.role = data['role']
    if 'location' in data: exp.location = data['location']
    if 'start_date' in data: exp.start_date = data['start_date']
    if 'end_date' in data: exp.end_date = data['end_date']
    if 'description' in data: exp.description = data['description']
    if 'is_current' in data: exp.is_current = bool(data['is_current'])
    if 'order_index' in data: exp.order_index = int(data['order_index'])
    
    db.session.commit()
    return jsonify({'message': 'Experience updated', 'experience': exp.to_dict()}), 200


# ─────────────────────────────────────────────
# DELETE /api/experience/<id>
# ─────────────────────────────────────────────
@experience_bp.route('/<int:exp_id>', methods=['DELETE'])
@jwt_required()
def delete_experience(exp_id):
    """Delete an experience item (admin only)."""
    exp = Experience.query.get_or_404(exp_id)
    db.session.delete(exp)
    db.session.commit()
    return jsonify({'message': 'Experience deleted'}), 200
