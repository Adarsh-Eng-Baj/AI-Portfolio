"""
routes/blog.py — Blog post endpoints.
Public reads, JWT-protected writes.
"""

import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models import BlogPost

blog_bp = Blueprint('blog', __name__)


def _slugify(text: str) -> str:
    """Convert title to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text


# ─────────────────────────────────────────────
# GET /api/blog
# ─────────────────────────────────────────────
@blog_bp.route('', methods=['GET'])
def list_posts():
    """List all published blog posts."""
    category = request.args.get('category')
    tag = request.args.get('tag')
    show_all = request.args.get('all', 'false').lower() == 'true'

    query = BlogPost.query
    if not show_all:
        query = query.filter(BlogPost.is_published == True)
    if category:
        query = query.filter(BlogPost.category.ilike(f'%{category}%'))

    posts = query.order_by(BlogPost.created_at.desc()).all()

    if tag:
        posts = [p for p in posts if tag.lower() in (p.tags or '').lower()]

    return jsonify({
        'posts': [p.to_dict() for p in posts],
        'total': len(posts)
    }), 200


# ─────────────────────────────────────────────
# GET /api/blog/<slug>
# ─────────────────────────────────────────────
@blog_bp.route('/<slug>', methods=['GET'])
def get_post(slug):
    """Get a single blog post by slug."""
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    # Increment view count
    post.views += 1
    db.session.commit()
    return jsonify({'post': post.to_dict()}), 200


# ─────────────────────────────────────────────
# POST /api/blog
# ─────────────────────────────────────────────
@blog_bp.route('', methods=['POST'])
@jwt_required()
def create_post():
    """Create a new blog post (admin only)."""
    data = request.get_json()

    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Title and content are required'}), 400

    slug = data.get('slug') or _slugify(data['title'])
    # Ensure unique slug
    existing = BlogPost.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{BlogPost.query.count() + 1}"

    post = BlogPost(
        title=data['title'].strip(),
        slug=slug,
        excerpt=data.get('excerpt', ''),
        content=data['content'],
        cover_image=data.get('cover_image', ''),
        tags=data.get('tags', ''),
        category=data.get('category', 'General'),
        is_published=data.get('is_published', False),
        read_time=data.get('read_time', 5),
    )

    db.session.add(post)
    db.session.commit()

    return jsonify({'message': 'Post created', 'post': post.to_dict()}), 201


# ─────────────────────────────────────────────
# PUT /api/blog/<id>
# ─────────────────────────────────────────────
@blog_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """Update a blog post (admin only)."""
    post = BlogPost.query.get_or_404(post_id)
    data = request.get_json() or {}

    if 'title' in data: post.title = data['title']
    if 'slug' in data: post.slug = data['slug']
    if 'excerpt' in data: post.excerpt = data['excerpt']
    if 'content' in data: post.content = data['content']
    if 'cover_image' in data: post.cover_image = data['cover_image']
    if 'tags' in data: post.tags = data['tags']
    if 'category' in data: post.category = data['category']
    if 'is_published' in data: post.is_published = bool(data['is_published'])
    if 'read_time' in data: post.read_time = int(data['read_time'])

    db.session.commit()
    return jsonify({'message': 'Post updated', 'post': post.to_dict()}), 200


# ─────────────────────────────────────────────
# DELETE /api/blog/<id>
# ─────────────────────────────────────────────
@blog_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """Delete a blog post (admin only)."""
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted'}), 200
