"""
routes/projects.py — Project CRUD endpoints.
Public reads, JWT-protected writes.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models import Project

projects_bp = Blueprint('projects', __name__)


# ─────────────────────────────────────────────
# GET /api/projects
# ─────────────────────────────────────────────
@projects_bp.route('', methods=['GET'])
def get_projects():
    """List all projects. Supports filtering by category and featured."""
    category = request.args.get('category')
    featured = request.args.get('featured')
    
    query = Project.query
    
    if category and category.lower() != 'all':
        query = query.filter(Project.category.ilike(f'%{category}%'))
    
    if featured is not None:
        query = query.filter(Project.featured == (featured.lower() == 'true'))
    
    projects = query.order_by(Project.featured.desc(), Project.created_at.desc()).all()
    
    return jsonify({
        'projects': [p.to_dict() for p in projects],
        'total': len(projects)
    }), 200


# ─────────────────────────────────────────────
# GET /api/projects/<id>
# ─────────────────────────────────────────────
@projects_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get a single project by ID."""
    project = Project.query.get_or_404(project_id)
    return jsonify({'project': project.to_dict()}), 200


# ─────────────────────────────────────────────
# POST /api/projects
# ─────────────────────────────────────────────
@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """Create a new project (admin only)."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Project title is required'}), 400
    
    # Handle tech_stack: accept list or comma-string
    tech_stack = data.get('tech_stack', '')
    if isinstance(tech_stack, list):
        tech_stack = ','.join(tech_stack)
    
    project = Project(
        title=title,
        description=data.get('description', ''),
        long_description=data.get('long_description', ''),
        tech_stack=tech_stack,
        demo_url=data.get('demo_url', ''),
        github_url=data.get('github_url', ''),
        image_url=data.get('image_url', ''),
        category=data.get('category', 'Web'),
        featured=data.get('featured', False),
        status=data.get('status', 'completed'),
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify({
        'message': 'Project created successfully',
        'project': project.to_dict()
    }), 201


# ─────────────────────────────────────────────
# PUT /api/projects/<id>
# ─────────────────────────────────────────────
@projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update an existing project (admin only)."""
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    # Update only the fields provided
    if 'title' in data:
        project.title = data['title'].strip()
    if 'description' in data:
        project.description = data['description']
    if 'long_description' in data:
        project.long_description = data['long_description']
    if 'tech_stack' in data:
        ts = data['tech_stack']
        project.tech_stack = ','.join(ts) if isinstance(ts, list) else ts
    if 'demo_url' in data:
        project.demo_url = data['demo_url']
    if 'github_url' in data:
        project.github_url = data['github_url']
    if 'image_url' in data:
        project.image_url = data['image_url']
    if 'category' in data:
        project.category = data['category']
    if 'featured' in data:
        project.featured = bool(data['featured'])
    if 'status' in data:
        project.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Project updated successfully',
        'project': project.to_dict()
    }), 200


# ─────────────────────────────────────────────
# DELETE /api/projects/<id>
# ─────────────────────────────────────────────
@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete a project (admin only)."""
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': 'Project deleted successfully'}), 200


# ─────────────────────────────────────────────
# GET /api/projects/categories
# ─────────────────────────────────────────────
@projects_bp.route('/meta/categories', methods=['GET'])
def get_categories():
    """Get all unique project categories."""
    categories = db.session.query(Project.category).distinct().all()
    return jsonify({
        'categories': ['All'] + [c[0] for c in categories if c[0]]
    }), 200
