"""
app/__init__.py — Flask application factory.
Creates and configures the Flask app with all extensions.
"""

import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail

# Initialize extensions (bound to app later via init_app)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()


def create_app(config_name=None):
    """Application factory — creates and returns a configured Flask app."""
    
    app = Flask(__name__)
    
    # ── Load Configuration ──────────────────────
    from app.config import config_map
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config_map.get(config_name, config_map['default']))
    
    # ── Initialize Extensions ───────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # ── Flask-Mail (Gmail SMTP) ──────────────────
    app.config['MAIL_SERVER']   = 'smtp.gmail.com'
    app.config['MAIL_PORT']     = 465
    app.config['MAIL_USE_TLS']  = False
    app.config['MAIL_USE_SSL']  = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', '')
    mail.init_app(app)

    # Share mail instance with email service
    from app.services import email_service
    email_service.mail = mail
    
    # CORS — allow all origins in dev, restrict in prod via CORS_ORIGINS env
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['*']),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })
    
    # ── Register Blueprints (routes) ────────────
    from app.routes.auth import auth_bp
    from app.routes.projects import projects_bp
    from app.routes.contact import contact_bp
    from app.routes.analytics import analytics_bp
    from app.routes.resume import resume_bp
    from app.routes.chatbot import chatbot_bp
    from app.routes.skills import skills_bp
    from app.routes.experience import experience_bp

    from app.routes.blog import blog_bp

    app.register_blueprint(auth_bp,      url_prefix='/api/auth')
    app.register_blueprint(projects_bp,  url_prefix='/api/projects')
    app.register_blueprint(contact_bp,   url_prefix='/api/contact')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(resume_bp,    url_prefix='/api/resume')
    app.register_blueprint(chatbot_bp,   url_prefix='/api/chat')
    app.register_blueprint(skills_bp,    url_prefix='/api/skills')
    app.register_blueprint(experience_bp, url_prefix='/api/experience')
    app.register_blueprint(blog_bp,      url_prefix='/api/blog')
    
    # ── Root API Info Route ─────────────────────
    @app.route('/api')
    def api_index():
        return jsonify({
            'message': 'Adarsh Sutar Portfolio API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'auth':      '/api/auth',
                'projects':  '/api/projects',
                'contact':   '/api/contact',
                'analytics': '/api/analytics',
                'resume':    '/api/resume/download',
                'chat':      '/api/chat',
                'skills':    '/api/skills',
                'experience': '/api/experience',
            }
        })
    
    # ── Health Check ────────────────────────────
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    # ── Global Error Handlers ───────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500
    
    # JWT error handlers
    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({'error': 'Authorization token missing', 'reason': reason}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({'error': 'Invalid token', 'reason': reason}), 422

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_data):
        return jsonify({'error': 'Token has expired'}), 401
    
    # ── Database Setup & Seeding ────────────────
    with app.app_context():
        db.create_all()
        _seed_database()
    
    return app


def _seed_database():
    """Seed the database with initial data on first run."""
    from app.models import User, Project, Skill, Experience, BlogPost
    import bcrypt
    from flask import current_app
    
    # Seed admin user
    if not User.query.filter_by(email=current_app.config['ADMIN_EMAIL']).first():
        hashed = bcrypt.hashpw(
            current_app.config['ADMIN_PASSWORD'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        admin = User(
            name=current_app.config['ADMIN_NAME'],
            email=current_app.config['ADMIN_EMAIL'],
            password_hash=hashed,
            role='admin'
        )
        db.session.add(admin)
        print(f"[OK] Admin user seeded: {current_app.config['ADMIN_EMAIL']}")
    
    # Seed projects (Adarsh Sutar's actual B.Tech CSE-AI projects)
    if Project.query.count() == 0:
        projects = [
            Project(
                title='AI-Powered Study Planner',
                description='Smart AI study schedule generator that adapts to your learning pace and exam dates.',
                long_description='An intelligent study planner that uses AI algorithms to generate personalized study schedules. It analyzes subject difficulty, available time slots, and exam deadlines to create optimized schedules. Features include task tracking, progress visualization, Pomodoro timer, and smart suggestions.',
                tech_stack='Python,Flask,JavaScript,HTML/CSS,SQLite,Chart.js',
                demo_url='#',
                github_url='https://github.com/adarshsutar',
                image_url='https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=600&q=80',
                category='AI/ML',
                featured=True,
                status='completed'
            ),
            Project(
                title='Smart ATS Resume Analyzer',
                description='NLP-powered resume analyzer that scores resumes against job descriptions using cosine similarity.',
                long_description='A professional ATS (Applicant Tracking System) analyzer that helps students optimize their resumes for job applications. Uses Natural Language Processing and cosine similarity to compare resumes against job descriptions, identifies missing keywords, and provides actionable improvement suggestions with an ATS compatibility score.',
                tech_stack='Python,Flask,NLTK,Scikit-learn,HTML/CSS,JavaScript',
                demo_url='#',
                github_url='https://github.com/adarshsutar',
                image_url='https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=600&q=80',
                category='AI/ML',
                featured=True,
                status='completed'
            ),
            Project(
                title='Kheti Mitra — AI Farming Assistant',
                description='Multilingual AI assistant for farmers with crop disease detection and recommendation system.',
                long_description='Kheti Mitra is a comprehensive AI-powered farming assistant designed for Indian farmers. Features include crop disease detection using CNN image classification, personalized crop recommendations based on soil and weather data, market price predictions, multilingual support (Hindi, Odia, English), and a secure farmer authentication system.',
                tech_stack='Python,FastAPI,TensorFlow,OpenCV,JavaScript,SQLite,JWT',
                demo_url='#',
                github_url='https://github.com/adarshsutar',
                image_url='https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=600&q=80',
                category='AI/ML',
                featured=True,
                status='completed'
            ),
            Project(
                title='Student Performance Analyzer',
                description='ML-based system to predict and analyze student academic performance with visual dashboard.',
                long_description='An ML-driven system for educational institutions to predict student performance, identify at-risk students early, and provide targeted interventions. Built with Java Spring Boot backend, Python ML service (scikit-learn), and a React dashboard. Uses multiple ML algorithms including Random Forest and Gradient Boosting.',
                tech_stack='Java,Spring Boot,Python,Scikit-learn,React,MySQL,REST API',
                demo_url='#',
                github_url='https://github.com/adarshsutar',
                image_url='https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&q=80',
                category='AI/ML',
                featured=False,
                status='completed'
            ),
            Project(
                title='Hand Gesture Recognition System',
                description='Real-time hand gesture recognition using OpenCV and ML for touchless interface control.',
                long_description='A computer vision project that uses OpenCV and machine learning to detect and classify hand gestures in real-time from webcam feed. Supports control of system volume, media playback, and cursor movement using gestures. Implements MediaPipe for landmark detection and a custom trained classifier for gesture recognition.',
                tech_stack='Python,OpenCV,MediaPipe,TensorFlow,NumPy',
                demo_url='#',
                github_url='https://github.com/adarshsutar',
                image_url='https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600&q=80',
                category='Computer Vision',
                featured=False,
                status='completed'
            ),
            Project(
                title='Portfolio Website (This Site)',
                description='Full-stack AI-powered portfolio with admin dashboard, chatbot, analytics & resume generator.',
                long_description='This very portfolio website — built with Flask backend, vanilla HTML/CSS/JS frontend. Features include an AI chatbot assistant, visitor analytics dashboard, dynamic project management, multi-language support (EN/HI), dark/light mode, JWT authentication, and automated PDF resume generation.',
                tech_stack='Python,Flask,SQLAlchemy,JavaScript,HTML/CSS,JWT,ReportLab',
                demo_url='#',
                github_url='https://github.com/adarshsutar',
                image_url='https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=600&q=80',
                category='Web',
                featured=False,
                status='completed'
            ),
        ]
        for p in projects:
            db.session.add(p)
        print("[OK] Projects seeded")
    
    # Seed skills
    if Skill.query.count() == 0:
        skills = [
            # Languages
            Skill(name='Python',      category='Languages',  proficiency=90, icon='🐍', order_index=1),
            Skill(name='JavaScript',  category='Languages',  proficiency=80, icon='🟨', order_index=2),
            Skill(name='C++',         category='Languages',  proficiency=75, icon='⚙️', order_index=3),
            Skill(name='Java',        category='Languages',  proficiency=70, icon='☕', order_index=4),
            Skill(name='HTML/CSS',    category='Languages',  proficiency=88, icon='🌐', order_index=5),
            # AI/ML
            Skill(name='TensorFlow',  category='AI/ML',      proficiency=75, icon='🧠', order_index=1),
            Skill(name='Scikit-learn',category='AI/ML',      proficiency=80, icon='📊', order_index=2),
            Skill(name='NumPy',       category='AI/ML',      proficiency=85, icon='🔢', order_index=3),
            Skill(name='Pandas',      category='AI/ML',      proficiency=82, icon='🐼', order_index=4),
            Skill(name='OpenCV',      category='AI/ML',      proficiency=70, icon='👁️', order_index=5),
            Skill(name='NLTK',        category='AI/ML',      proficiency=72, icon='💬', order_index=6),
            # Frameworks
            Skill(name='Flask',       category='Frameworks', proficiency=88, icon='🌶️', order_index=1),
            Skill(name='FastAPI',     category='Frameworks', proficiency=75, icon='⚡', order_index=2),
            Skill(name='Spring Boot', category='Frameworks', proficiency=60, icon='🍃', order_index=3),
            Skill(name='React',       category='Frameworks', proficiency=65, icon='⚛️', order_index=4),
            # Databases
            Skill(name='MySQL',       category='Databases',  proficiency=78, icon='🐬', order_index=1),
            Skill(name='PostgreSQL',  category='Databases',  proficiency=70, icon='🐘', order_index=2),
            Skill(name='SQLite',      category='Databases',  proficiency=85, icon='💾', order_index=3),
            Skill(name='MongoDB',     category='Databases',  proficiency=65, icon='🍃', order_index=4),
            # Cloud
            Skill(name='AWS',         category='Cloud',      proficiency=68, icon='☁️', order_index=1),
            Skill(name='EC2/S3',      category='Cloud',      proficiency=65, icon='📦', order_index=2),
            Skill(name='Lambda',      category='Cloud',      proficiency=60, icon='⚡', order_index=3),
            # Tools
            Skill(name='Git/GitHub',  category='Tools',      proficiency=85, icon='🐙', order_index=1),
            Skill(name='VS Code',     category='Tools',      proficiency=90, icon='💻', order_index=2),
            Skill(name='Jupyter',     category='Tools',      proficiency=88, icon='📓', order_index=3),
            Skill(name='Docker',      category='Tools',      proficiency=55, icon='🐳', order_index=4),
            Skill(name='Postman',     category='Tools',      proficiency=80, icon='📮', order_index=5),
        ]
        for s in skills:
            db.session.add(s)
        print("[OK] Skills seeded")
    
    # Seed experience
    if Experience.query.count() == 0:
        experiences = [
            Experience(
                type='education',
                company='Gandhi Institute of Excellent Technocrats (GIET)',
                role='B.Tech in Computer Science & Engineering (AI)',
                location='Ghangapatna, Bhubaneswar, Odisha',
                start_date='Aug 2023',
                end_date='May 2027',
                description='Currently pursuing B.Tech in CSE with specialization in Artificial Intelligence. Core subjects include Machine Learning, Data Structures & Algorithms, Computer Vision, NLP, Cloud Computing (AWS), and Software Engineering. SGPA: 8.44 (last semester)',
                is_current=True,
                order_index=1
            ),
            Experience(
                type='education',
                company='Khaira Higher Secondary School',
                role='Higher Secondary Certificate (HSC) — PCM-IT',
                location='Khaira, Balasore, Odisha',
                start_date='Jun 2021',
                end_date='May 2023',
                description='Completed HSC with Physics, Chemistry, Mathematics, and Information Technology (PCM-IT).',
                is_current=False,
                order_index=2
            ),
            Experience(
                type='work',
                company='Self-Initiated Projects & Open Source',
                role='Full-Stack & AI Developer',
                location='Remote',
                start_date='Jan 2024',
                end_date='Present',
                description='Built multiple end-to-end projects combining AI/ML backends with modern web frontends. Focused on practical applications of machine learning and cloud computing for real-world problems.',
                is_current=True,
                order_index=3
            ),
        ]
        for ex in experiences:
            db.session.add(ex)
        print("[OK] Experience seeded")
    
    # Seed sample blog posts
    if BlogPost.query.count() == 0:
        posts = [
            BlogPost(
                title='Getting Started with Machine Learning in Python',
                slug='getting-started-with-ml-python',
                excerpt='A beginner-friendly guide to understanding the fundamentals of Machine Learning using Python, Scikit-learn and real datasets.',
                content='## Introduction\n\nMachine Learning is one of the most exciting fields in tech today. In this post, I walk you through the basics...\n\n## What is ML?\n\nMachine Learning allows computers to learn from data without being explicitly programmed...\n\n## Setting Up\n\n```python\npip install scikit-learn pandas numpy\n```\n\n## Your First Model\n\nLet\'s build a simple classifier...\n\nStay tuned for part 2!',
                cover_image='https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80',
                tags='Python,Machine Learning,Scikit-learn,Beginner',
                category='AI/ML',
                is_published=True,
                read_time=8
            ),
            BlogPost(
                title='AWS EC2 vs Lambda: When to Use What?',
                slug='aws-ec2-vs-lambda-guide',
                excerpt='A practical comparison of AWS EC2 and Lambda to help you choose the right compute option for your next cloud project.',
                content='## EC2 vs Lambda\n\nTwo of the most popular AWS compute services are EC2 and Lambda. But when should you use each?\n\n## AWS EC2\n\nEC2 (Elastic Compute Cloud) gives you a full virtual server...\n\n## AWS Lambda\n\nLambda is a serverless compute service that runs your code only when needed...\n\n## My Recommendation\n\nFor long-running apps use EC2. For event-driven microservices, Lambda is 🔥',
                cover_image='https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80',
                tags='AWS,Cloud,EC2,Lambda,Serverless',
                category='Cloud',
                is_published=True,
                read_time=6
            ),
            BlogPost(
                title='Building a Flask REST API with JWT Authentication',
                slug='flask-rest-api-jwt',
                excerpt='Step-by-step tutorial on building a production-ready Flask REST API with JWT tokens, CORS, and SQLAlchemy.',
                content='## Flask REST API\n\nIn this tutorial, we build a secure Flask API from scratch...\n\n## Setup\n\n```python\npip install flask flask-jwt-extended flask-sqlalchemy\n```\n\n## Creating the App Factory\n\n...\n\n## Adding JWT Auth\n\n...',
                cover_image='https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80',
                tags='Flask,Python,JWT,REST API,Backend',
                category='Web Dev',
                is_published=True,
                read_time=10
            ),
        ]
        for post in posts:
            db.session.add(post)
        print("[OK] Blog posts seeded")
    
    db.session.commit()
