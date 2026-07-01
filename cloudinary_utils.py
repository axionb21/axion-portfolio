import cloudinary
import cloudinary.uploader
from flask import current_app


def init_cloudinary(app):
    cloudinary.config(
        cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=app.config["CLOUDINARY_API_KEY"],
        api_secret=app.config["CLOUDINARY_API_SECRET"],
        secure=True,
    )


def upload_file(file_storage, folder="axion-b21"):
    """
    Uploads a file (image, pdf, etc.) to Cloudinary and returns its public URL.
    Returns None if no file was given, so callers can safely skip empty upload fields.
    """
    if not file_storage or file_storage.filename == "":
        return None
    result = cloudinary.uploader.upload(
        file_storage,
        folder=folder,
        resource_type="auto",   # auto-detects image vs pdf vs raw file
    )
    return result.get("secure_url")
