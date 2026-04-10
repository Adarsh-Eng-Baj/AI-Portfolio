"""
config.py — Application configuration for different environments.
Uses python-dotenv to load .env file automatically.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration shared across all environments."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-xyz123'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production-abc456'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # CORS — allowed origins for the frontend
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # OpenAI (optional — chatbot uses fallback if not set)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    
    # Admin seeding
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@portfolio.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
    ADMIN_NAME = os.environ.get('ADMIN_NAME', 'Adarsh Sutar')


class DevelopmentConfig(Config):
    """Development configuration — uses SQLite (no setup required)."""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(BASE_DIR, '..', 'portfolio.db')}"


class ProductionConfig(Config):
    """Production configuration — uses PostgreSQL (Supabase)."""
    
    DEBUG = False
    
    # Supabase / PostgreSQL connection string
    # Format: postgresql://user:password@host:port/dbname
    _db_url = os.environ.get('DATABASE_URL', '')
    
    # Render's DATABASE_URL uses postgres:// prefix; SQLAlchemy needs postgresql://
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///portfolio_prod.db'


class TestingConfig(Config):
    """Testing configuration — uses in-memory SQLite."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Config map for easy selection
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
