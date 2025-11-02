"""Configuration settings for Gmail Attachment Downloader."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration."""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database settings
    basedir = Path(__file__).resolve().parent

    # Database configuration
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite')  # sqlite, mysql, postgresql, mssql

    if DB_TYPE == 'mysql':
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '3306')
        DB_NAME = os.getenv('DB_NAME', 'gmail_downloader')
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DATABASE_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    elif DB_TYPE == 'postgresql':
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        DB_NAME = os.getenv('DB_NAME', 'gmail_downloader')
        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    elif DB_TYPE == 'mssql':
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '1433')
        DB_NAME = os.getenv('DB_NAME', 'gmail_downloader')
        DB_USER = os.getenv('DB_USER', 'sa')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DATABASE_URL = f'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server'

    else:  # sqlite (default)
        DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///{basedir / 'instance' / 'email_downloader.db'}")

    # Handle legacy PostgreSQL URL format for Heroku
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload settings
    ATTACHMENT_FOLDER = os.getenv('ATTACHMENT_FOLDER', str(basedir / 'static' / 'attachments'))
    MAX_ATTACHMENT_SIZE_MB = int(os.getenv('MAX_ATTACHMENT_SIZE_MB', '25'))
    MAX_CONTENT_LENGTH = MAX_ATTACHMENT_SIZE_MB * 1024 * 1024

    # Gmail API settings
    GMAIL_CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
    GMAIL_TOKEN_FILE = os.getenv('GMAIL_TOKEN_FILE', 'token.pickle')

    # IMAP settings (fallback)
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
    IMAP_PORT = int(os.getenv('IMAP_PORT', '993'))

    # Security settings
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Pagination
    POSTS_PER_PAGE = 20

    # Logging
    LOG_TO_STDOUT = os.getenv('LOG_TO_STDOUT', 'False').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
