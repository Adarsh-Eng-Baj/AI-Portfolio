"""
models.py — SQLAlchemy database models.
All tables for the portfolio application are defined here.
"""

from datetime import datetime
from app import db


# ─────────────────────────────────────────────
# User Model (Admin authentication)
# ─────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='admin')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }


# ─────────────────────────────────────────────
# Project Model
# ─────────────────────────────────────────────
class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    long_description = db.Column(db.Text)
    tech_stack = db.Column(db.String(500))       # comma-separated e.g. "Python, Flask, React"
    demo_url = db.Column(db.String(300))
    github_url = db.Column(db.String(300))
    image_url = db.Column(db.String(300))
    category = db.Column(db.String(100))         # e.g. "AI/ML", "Web", "Mobile"
    featured = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='completed')  # completed | in-progress | planned
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'long_description': self.long_description,
            'tech_stack': self.tech_stack.split(',') if self.tech_stack else [],
            'demo_url': self.demo_url,
            'github_url': self.github_url,
            'image_url': self.image_url,
            'category': self.category,
            'featured': self.featured,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }


# ─────────────────────────────────────────────
# Skill Model
# ─────────────────────────────────────────────
class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))    # Languages | Frameworks | AI/ML | Tools | Databases
    proficiency = db.Column(db.Integer, default=75)  # 0-100
    icon = db.Column(db.String(100))        # devicon class or emoji
    order_index = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'proficiency': self.proficiency,
            'icon': self.icon,
            'order_index': self.order_index,
        }


# ─────────────────────────────────────────────
# Experience Model (Education + Work)
# ─────────────────────────────────────────────
class Experience(db.Model):
    __tablename__ = 'experiences'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), default='education')  # education | work
    company = db.Column(db.String(200))
    role = db.Column(db.String(200))
    location = db.Column(db.String(200))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    description = db.Column(db.Text)
    is_current = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'company': self.company,
            'role': self.role,
            'location': self.location,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'description': self.description,
            'is_current': self.is_current,
        }


# ─────────────────────────────────────────────
# Contact Message Model
# ─────────────────────────────────────────────
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
        }


# ─────────────────────────────────────────────
# Analytics Event Model
# ─────────────────────────────────────────────
class AnalyticsEvent(db.Model):
    __tablename__ = 'analytics_events'

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(200))
    session_id = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    referrer = db.Column(db.String(300))
    duration = db.Column(db.Integer)        # page view duration in seconds
    country = db.Column(db.String(100))
    device_type = db.Column(db.String(50))  # mobile | tablet | desktop
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'page': self.page,
            'session_id': self.session_id,
            'device_type': self.device_type,
            'duration': self.duration,
            'created_at': self.created_at.isoformat(),
        }


# ─────────────────────────────────────────────
# Blog Post Model
# ─────────────────────────────────────────────
class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False)
    excerpt = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(500))
    tags = db.Column(db.String(500))          # comma-separated
    category = db.Column(db.String(100))
    is_published = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    read_time = db.Column(db.Integer, default=5)  # minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'content': self.content,
            'cover_image': self.cover_image,
            'tags': self.tags.split(',') if self.tags else [],
            'category': self.category,
            'is_published': self.is_published,
            'views': self.views,
            'read_time': self.read_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
