from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class AdminUser(UserMixin, db.Model):
    """The single admin account. Password is hashed, never stored as plain text."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))          # e.g. "Research Project"
    description = db.Column(db.Text)
    tags = db.Column(db.String(300))               # comma-separated: "Flask,SocketIO,SQLite"
    github_url = db.Column(db.String(300))
    live_demo_url = db.Column(db.String(300))
    image_url = db.Column(db.String(500))           # Cloudinary link
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def tag_list(self):
        return [t.strip() for t in (self.tags or "").split(",") if t.strip()]


class Writeup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False)   # url path, e.g. linux-privesc
    category = db.Column(db.String(50))              # Web / AD / Linux / Windows / Cloud / Malware / Crypto
    content = db.Column(db.Text)                      # markdown text
    file_url = db.Column(db.String(500))               # optional attached file on Cloudinary
    ctf_event = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ResearchPaper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    abstract = db.Column(db.Text)
    status = db.Column(db.String(30), default="Draft")   # Draft / Published
    pdf_url = db.Column(db.String(500))
    citation_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False)
    content = db.Column(db.Text)
    cover_image_url = db.Column(db.String(500))
    published_at = db.Column(db.DateTime, default=datetime.utcnow)


class Lab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default="Building")  # Building / Active / Archived


class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    issuer = db.Column(db.String(150))
    badge_image_url = db.Column(db.String(500))
    date_earned = db.Column(db.String(30))
    credential_url = db.Column(db.String(300))


class SiteSettings(db.Model):
    """Single-row table for editable homepage text, resume link, contact info."""
    id = db.Column(db.Integer, primary_key=True)
    tagline = db.Column(db.String(300), default="Ethical Hacker | Offensive Security Researcher | CTF Player")
    about_text = db.Column(db.Text, default="")
    resume_url = db.Column(db.String(500))
    github_url = db.Column(db.String(300))
    linkedin_url = db.Column(db.String(300))
    twitter_url = db.Column(db.String(300))
    discord_handle = db.Column(db.String(100))
    email = db.Column(db.String(150))
    location = db.Column(db.String(150))
