from flask import Blueprint, render_template, abort, jsonify, request
import markdown as md_lib

from models import (
    Project, Writeup, ResearchPaper, BlogPost, Lab, Certification, SiteSettings
)

public_bp = Blueprint("public", __name__)


def get_settings():
    return SiteSettings.query.first()


def get_stats():
    return {
        "projects": Project.query.count(),
        "writeups": Writeup.query.count(),
        "research": ResearchPaper.query.count(),
        "blogs": BlogPost.query.count(),
        "certifications": Certification.query.count(),
    }


@public_bp.route("/")
def index():
    recent_writeups = Writeup.query.order_by(Writeup.created_at.desc()).limit(3).all()
    recent_blogs = BlogPost.query.order_by(BlogPost.published_at.desc()).limit(3).all()
    return render_template(
        "index.html",
        settings=get_settings(),
        stats=get_stats(),
        recent_writeups=recent_writeups,
        recent_blogs=recent_blogs,
    )


@public_bp.route("/projects")
def projects():
    items = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("projects.html", items=items, settings=get_settings())


@public_bp.route("/writeups")
def writeups():
    category = request.args.get("category")
    q = Writeup.query
    if category:
        q = q.filter_by(category=category)
    items = q.order_by(Writeup.created_at.desc()).all()
    categories = ["Web", "Linux", "Windows", "AD", "Cloud", "Cryptography", "Reverse Engineering", "Forensics", "Malware", "OSINT"]
    return render_template("writeups.html", items=items, categories=categories, active_category=category, settings=get_settings())


@public_bp.route("/writeups/<slug>")
def writeup_detail(slug):
    item = Writeup.query.filter_by(slug=slug).first_or_404()
    html_content = md_lib.markdown(item.content or "", extensions=["fenced_code", "tables"])
    return render_template("writeup_detail.html", item=item, html_content=html_content, settings=get_settings())


@public_bp.route("/research")
def research():
    items = ResearchPaper.query.order_by(ResearchPaper.created_at.desc()).all()
    return render_template("research.html", items=items, settings=get_settings())


@public_bp.route("/blogs")
def blogs():
    items = BlogPost.query.order_by(BlogPost.published_at.desc()).all()
    return render_template("blogs.html", items=items, settings=get_settings())


@public_bp.route("/blogs/<slug>")
def blog_detail(slug):
    item = BlogPost.query.filter_by(slug=slug).first_or_404()
    html_content = md_lib.markdown(item.content or "", extensions=["fenced_code", "tables"])
    return render_template("blog_detail.html", item=item, html_content=html_content, settings=get_settings())


@public_bp.route("/labs")
def labs():
    items = Lab.query.all()
    return render_template("labs.html", items=items, settings=get_settings())


@public_bp.route("/certifications")
def certifications():
    items = Certification.query.all()
    return render_template("certifications.html", items=items, settings=get_settings())


@public_bp.route("/contact")
def contact():
    return render_template("contact.html", settings=get_settings())


# --- Terminal widget backend ---
# The homepage terminal sends commands here (e.g. "writeups", "whoami")
# and gets back JSON so it can print results without a full page reload.
@public_bp.route("/api/terminal", methods=["POST"])
def terminal_command():
    cmd = (request.json or {}).get("command", "").strip().lower()
    settings = get_settings()

    responses = {
        "whoami": "guest@axion-b21 — you are viewing a public terminal session",
        "about": (settings.about_text or "Cyber Security Student. Offensive Security Enthusiast.")
        if settings else "Cyber Security Student.",
        "github": settings.github_url if settings else "",
        "linkedin": settings.linkedin_url if settings else "",
        "resume": settings.resume_url if settings else "",
        "contact": settings.email if settings else "",
    }

    if cmd in responses:
        return jsonify({"output": responses[cmd]})

    if cmd == "writeups":
        items = Writeup.query.order_by(Writeup.created_at.desc()).limit(10).all()
        lines = [f"{i+1}. {w.title}  ->  open {w.slug}" for i, w in enumerate(items)]
        return jsonify({"output": "\n".join(lines) or "No writeups published yet."})

    if cmd.startswith("open "):
        slug = cmd.replace("open ", "").strip()
        match = Writeup.query.filter(Writeup.slug.ilike(f"%{slug}%")).first()
        if match:
            return jsonify({"redirect": f"/writeups/{match.slug}"})
        return jsonify({"output": f"No writeup matching '{slug}'"})

    if cmd == "help":
        return jsonify({"output": "Commands: about, whoami, writeups, projects, research, blogs, labs, resume, github, linkedin, contact, clear"})

    if cmd in ("projects", "research", "blogs", "labs", "certifications"):
        return jsonify({"redirect": f"/{cmd}"})

    return jsonify({"output": f"command not found: {cmd}  (type 'help')"})
