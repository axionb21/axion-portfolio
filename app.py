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

    # Lets admin/list.html do getattr(item, cfg.list_display) since the
    # registry pattern needs to read a different field per content type.
    app.jinja_env.globals["getattr"] = getattr

    with app.app_context():
        db.create_all()
        _ensure_settings_row()

    return app


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
    """
    Run once after first deploy:  flask --app app.py init-admin
    Creates the admin account from ADMIN_USER / ADMIN_PASS env vars.
    Safe to re-run - does nothing if an admin already exists.
    """
    if AdminUser.query.first():
        print("Admin already exists - skipping. Delete the row manually first if you need to reset it.")
        return
    admin = AdminUser(username=app.config["ADMIN_USER"])
    admin.set_password(app.config["ADMIN_PASS"])
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user '{admin.username}' created.")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
