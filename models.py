"""Database models for Gmail Attachment Downloader."""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Index

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    attachments = db.relationship('Attachment', backref='owner', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def attachment_count(self):
        return len(self.attachments)

    @property
    def total_size(self):
        return sum(att.size for att in self.attachments if att.size)

class Attachment(db.Model):
    """Attachment model for downloaded files."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Email metadata
    email_from = db.Column(db.String(300), index=True)
    subject = db.Column(db.String(500))
    date_received = db.Column(db.DateTime)

    # File information
    filename = db.Column(db.String(500), nullable=False)
    filepath = db.Column(db.String(1000), nullable=False)
    filetype = db.Column(db.String(50), index=True)
    size = db.Column(db.BigInteger, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Attachment {self.filename}>'

    @property
    def formatted_size(self):
        """Return human-readable file size."""
        if not self.size:
            return "0 B"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size < 1024.0:
                return f"{self.size:.1f} {unit}"
            self.size /= 1024.0
        return f"{self.size:.1f} TB"

    @property
    def file_extension(self):
        """Return file extension."""
        return self.filetype or 'unknown'

    @property
    def is_image(self):
        """Check if file is an image."""
        image_types = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'}
        return self.filetype.lower() in image_types

    @property
    def is_document(self):
        """Check if file is a document."""
        doc_types = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf'}
        return self.filetype.lower() in doc_types

    @property
    def is_archive(self):
        """Check if file is an archive."""
        archive_types = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2'}
        return self.filetype.lower() in archive_types

# Database indexes for better performance
Index('idx_attachment_user_date', Attachment.user_id, Attachment.created_at.desc())
Index('idx_attachment_filename', Attachment.filename)
Index('idx_attachment_type', Attachment.filetype)
Index('idx_user_email', User.email)
