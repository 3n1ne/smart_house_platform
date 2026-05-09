from flask import Blueprint


search_bp = Blueprint("search", __name__)


@search_bp.get("/ping")
def ping():
    return {"module": "search", "status": "ready"}
