import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

from config import Config
from models import db, AdminUser, SiteSettings
from cloudinary_utils import init_cloudinary

load_dotenv()

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = f"admin.login"
    init_cloudinary(app)

    from routes.public import public_bp
    from routes.admin import build_admin_blueprint

    app.register_blueprint(public_bp)
    app.register_blueprint(build_admin_blueprint(app.config["ADMIN_URL_PATH"]))

    app.jinja_env.globals["getattr"] = getattr

    with app.app_context():
        db.create_all()
        _ensure_settings_row()
        _ensure_admin_account(app)

    return app


def _ensure_admin_account(app):
    """
    Creates the admin login automatically on startup if none exists yet,
    using ADMIN_USER / ADMIN_PASS from environment variables.
    This removes the need for Shell access (not available on free tier).
    """
    if AdminUser.query.first():
        return
    admin = AdminUser(username=app.config["ADMIN_USER"])
    admin.set_password(app.config["ADMIN_PASS"])
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user '{admin.username}' created automatically on startup.")


def _ensure_settings_row():
    """SiteSettings always has exactly one row - create it once if missing."""
    if SiteSettings.query.first() is None:
        db.session.add(SiteSettings())
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


app = create_app()


@app.cli.command("init-admin")
def init_admin():
    """Kept for local development use only - not needed on Render free tier."""
    if AdminUser.query.first():
        print("Admin already exists - skipping.")
        return
    admin = AdminUser(username=app.config["ADMIN_USER"])
    admin.set_password(app.config["ADMIN_PASS"])
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user '{admin.username}' created.")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
