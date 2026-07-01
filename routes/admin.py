from flask import (
    Blueprint, render_template, redirect, url_for, request, flash, abort
)
from flask_login import login_user, logout_user, login_required, current_user

from models import (
    db, AdminUser, Project, Writeup, ResearchPaper, BlogPost, Lab,
    Certification, SiteSettings
)
from cloudinary_utils import upload_file


# --- Registry describing every editable content type ---
# Adding a new admin-editable section later only means adding one entry here.
REGISTRY = {
    "projects": {
        "model": Project,
        "label": "Projects",
        "list_display": "title",
        "fields": [
            ("title", "text"), ("category", "text"), ("description", "textarea"),
            ("tags", "text"), ("github_url", "text"), ("live_demo_url", "text"),
            ("image", "file"),
        ],
        "file_field_map": {"image": "image_url"},
    },
    "writeups": {
        "model": Writeup,
        "label": "Writeups",
        "list_display": "title",
        "fields": [
            ("title", "text"), ("slug", "text"), ("category", "text"),
            ("ctf_event", "text"), ("content", "textarea"), ("file", "file"),
        ],
        "file_field_map": {"file": "file_url"},
    },
    "research": {
        "model": ResearchPaper,
        "label": "Research Papers",
        "list_display": "title",
        "fields": [
            ("title", "text"), ("abstract", "textarea"),
            ("status", "select:Draft,Published"), ("citation_text", "textarea"),
            ("pdf", "file"),
        ],
        "file_field_map": {"pdf": "pdf_url"},
    },
    "blogs": {
        "model": BlogPost,
        "label": "Blogs",
        "list_display": "title",
        "fields": [
            ("title", "text"), ("slug", "text"), ("content", "textarea"),
            ("cover", "file"),
        ],
        "file_field_map": {"cover": "cover_image_url"},
    },
    "labs": {
        "model": Lab,
        "label": "Labs",
        "list_display": "name",
        "fields": [
            ("name", "text"), ("description", "textarea"),
            ("status", "select:Building,Active,Archived"),
        ],
        "file_field_map": {},
    },
    "certifications": {
        "model": Certification,
        "label": "Certifications",
        "list_display": "name",
        "fields": [
            ("name", "text"), ("issuer", "text"), ("date_earned", "text"),
            ("credential_url", "text"), ("badge", "file"),
        ],
        "file_field_map": {"badge": "badge_image_url"},
    },
}


def build_admin_blueprint(url_prefix):
    """
    url_prefix comes from ADMIN_URL_PATH env var, so the panel lives at a
    secret path like /axen-ctrl-7f3q instead of the guessable /admin.
    """
    admin_bp = Blueprint("admin", __name__, url_prefix=f"/{url_prefix}")

    @admin_bp.context_processor
    def inject_registry():
        # Makes `registry` available in every admin template's sidebar nav,
        # without needing to pass it explicitly from each route.
        return {"registry": REGISTRY}

    # ---------- Auth ----------
    @admin_bp.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("admin.dashboard"))
        if request.method == "POST":
            user = AdminUser.query.filter_by(username=request.form.get("username")).first()
            if user and user.check_password(request.form.get("password", "")):
                login_user(user)
                return redirect(url_for("admin.dashboard"))
            flash("Invalid credentials.", "error")
        return render_template("admin/login.html")

    @admin_bp.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("admin.login"))

    # ---------- Dashboard ----------
    @admin_bp.route("/")
    @login_required
    def dashboard():
        counts = {key: cfg["model"].query.count() for key, cfg in REGISTRY.items()}
        return render_template("admin/dashboard.html", counts=counts, registry=REGISTRY)

    # ---------- Site settings (homepage text, resume, socials) ----------
    @admin_bp.route("/settings", methods=["GET", "POST"])
    @login_required
    def settings():
        s = SiteSettings.query.first()
        if request.method == "POST":
            for field in ["tagline", "about_text", "resume_url", "github_url",
                          "linkedin_url", "twitter_url", "discord_handle", "email", "location"]:
                setattr(s, field, request.form.get(field, ""))
            db.session.commit()
            flash("Settings updated.", "success")
            return redirect(url_for("admin.settings"))
        return render_template("admin/settings.html", s=s)

    # ---------- Generic list ----------
    @admin_bp.route("/<section>")
    @login_required
    def list_items(section):
        cfg = REGISTRY.get(section)
        if not cfg:
            abort(404)
        items = cfg["model"].query.all()
        return render_template("admin/list.html", section=section, cfg=cfg, items=items)

    # ---------- Generic create/edit ----------
    @admin_bp.route("/<section>/new", methods=["GET", "POST"])
    @admin_bp.route("/<section>/<int:item_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_item(section, item_id=None):
        cfg = REGISTRY.get(section)
        if not cfg:
            abort(404)
        model = cfg["model"]
        item = model.query.get(item_id) if item_id else model()

        if request.method == "POST":
            for field_name, field_type in cfg["fields"]:
                if field_type == "file":
                    uploaded = request.files.get(field_name)
                    url = upload_file(uploaded, folder=f"axion-b21/{section}")
                    if url:
                        db_field = cfg["file_field_map"][field_name]
                        setattr(item, db_field, url)
                else:
                    value = request.form.get(field_name, "")
                    setattr(item, field_name, value)
            if not item_id:
                db.session.add(item)
            db.session.commit()
            flash(f"{cfg['label']} saved.", "success")
            return redirect(url_for("admin.list_items", section=section))

        return render_template("admin/form.html", section=section, cfg=cfg, item=item)

    # ---------- Generic delete ----------
    @admin_bp.route("/<section>/<int:item_id>/delete", methods=["POST"])
    @login_required
    def delete_item(section, item_id):
        cfg = REGISTRY.get(section)
        if not cfg:
            abort(404)
        item = cfg["model"].query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        flash(f"{cfg['label']} deleted.", "success")
        return redirect(url_for("admin.list_items", section=section))

    return admin_bp
