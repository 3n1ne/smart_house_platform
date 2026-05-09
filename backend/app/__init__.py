from flask import Flask, send_from_directory

from .api import register_blueprints
from .config import config_by_name
from .extensions import init_extensions
from .services.bootstrap import seed_roles


def create_app(config_name: str = "development", config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    if config_overrides:
        app.config.update(config_overrides)

    init_extensions(app)
    register_blueprints(app)

    from . import models  # noqa: F401
    from .extensions import db

    if app.config.get("AUTO_CREATE_DB", True):
        with app.app_context():
            db.create_all()
            seed_roles()

    @app.get("/health")
    def health_check():
        return {"status": "ok", "service": "backend"}

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    return app
