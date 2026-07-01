import os

class Config:
    # --- Core Flask ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me")

    # --- Database ---
    # Render gives DATABASE_URL starting with "postgres://" but SQLAlchemy
    # needs "postgresql://" - this line fixes that mismatch automatically.
    _db_url = os.environ.get("DATABASE_URL", "sqlite:///local.db")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Admin account (set these in Render's Environment tab, not here) ---
    ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
    ADMIN_PASS = os.environ.get("ADMIN_PASS", "change-me-immediately")

    # Hidden admin path, e.g. ADMIN_URL_PATH=axen-ctrl-7f3q
    # means your panel lives at /axen-ctrl-7f3q/login instead of a guessable /admin
    ADMIN_URL_PATH = os.environ.get("ADMIN_URL_PATH", "admin")

    # --- Cloudinary (file storage that survives restarts) ---
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB upload limit per file
