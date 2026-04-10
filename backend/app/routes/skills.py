"""
routes/skills.py — Technical skills endpoints.
Public reads, JWT-protected writes.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models import Skill

skills_bp = Blueprint('skills', __name__)


# ─────────────────────────────────────────────
# GET /api/skills
# ─────────────────────────────────────────────
@skills_bp.route('', methods=['GET'])
def get_skills():
    """List all skills grouped by category or as a flat list."""
    category = request.args.get('category')
    
    query = Skill.query
    if category:
        query = query.filter(Skill.category.ilike(f'%{category}%'))
    
    skills = query.order_by(Skill.order_index.asc(), Skill.name.asc()).all()
    
    return jsonify({
        'skills': [s.to_dict() for s in skills],
        'total': len(skills)
    }), 200


# ─────────────────────────────────────────────
# POST /api/skills
# ─────────────────────────────────────────────
@skills_bp.route('', methods=['POST'])
@jwt_required()
def create_skill():
    """Create a new skill (admin only)."""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Skill name is required'}), 400
    
    skill = Skill(
        name=data['name'].strip(),
        category=data.get('category', 'Tools'),
        proficiency=data.get('proficiency', 75),
        icon=data.get('icon', '⭐'),
        order_index=data.get('order_index', 0)
    )
    
    db.session.add(skill)
    db.session.commit()
    
    return jsonify({'message': 'Skill created', 'skill': skill.to_dict()}), 201


# ─────────────────────────────────────────────
# PUT /api/skills/<id>
# ─────────────────────────────────────────────
@skills_bp.route('/<int:skill_id>', methods=['PUT'])
@jwt_required()
def update_skill(skill_id):
    """Update an existing skill (admin only)."""
    skill = Skill.query.get_or_404(skill_id)
    data = request.get_json() or {}
    
    if 'name' in data: skill.name = data['name']
    if 'category' in data: skill.category = data['category']
    if 'proficiency' in data: skill.proficiency = data['proficiency']
    if 'icon' in data: skill.icon = data['icon']
    if 'order_index' in data: skill.order_index = data['order_index']
    
    db.session.commit()
    return jsonify({'message': 'Skill updated', 'skill': skill.to_dict()}), 200


# ─────────────────────────────────────────────
# DELETE /api/skills/<id>
# ─────────────────────────────────────────────
@skills_bp.route('/<int:skill_id>', methods=['DELETE'])
@jwt_required()
def delete_skill(skill_id):
    """Delete a skill (admin only)."""
    skill = Skill.query.get_or_404(skill_id)
    db.session.delete(skill)
    db.session.commit()
    return jsonify({'message': 'Skill deleted'}), 200
