from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from sqlalchemy import or_

from app.extensions import db
from app.models.base import utc_now
from app.models.news import News
from app.schemas.news import serialize_news
from app.utils.api_response import error_response, success_response
from app.utils.auth import get_current_user, roles_required
from app.utils.operation_log import log_operation


news_bp = Blueprint("news", __name__)


def _get_news_or_404(news_id):
    news = db.session.get(News, news_id)
    if news is None:
        return None, error_response("resource not found", code=4004, status=404)
    return news, None


def _can_manage_news(user, role, news):
    return role == "admin" or (role == "landlord" and news.author_id == user.id)


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 50)
    pagination = query.paginate(page=page, per_page=page_size)
    return success_response(
        {
            "items": [serialize_news(item) for item in pagination.items],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": pagination.total,
            },
        }
    )


@news_bp.get("")
def list_published_news():
    query = News.query.filter(News.status == "published")

    keyword = request.args.get("keyword")
    if keyword:
        like_value = f"%{keyword}%"
        query = query.filter(or_(News.title.like(like_value), News.content.like(like_value)))

    return _paginate(query.order_by(News.published_at.desc(), News.created_at.desc()))


@news_bp.get("/mine")
@roles_required("landlord", "admin")
def list_my_news():
    user = get_current_user()
    role = get_jwt().get("role")
    query = News.query

    if role == "landlord":
        query = query.filter(News.author_id == user.id)

    status = request.args.get("status")
    keyword = request.args.get("keyword")
    if status:
        query = query.filter(News.status == status)
    if keyword:
        like_value = f"%{keyword}%"
        query = query.filter(or_(News.title.like(like_value), News.content.like(like_value)))

    return _paginate(query.order_by(News.created_at.desc()))


@news_bp.post("")
@roles_required("landlord", "admin")
def create_news():
    user = get_current_user()
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    content = (payload.get("content") or "").strip()
    status = payload.get("status") or "draft"

    if not title or not content:
        return error_response(
            "validation error",
            code=4001,
            errors={"news": ["title and content are required"]},
        )
    if status not in {"draft", "published"}:
        return error_response(
            "validation error",
            code=4001,
            errors={"status": ["status must be draft or published"]},
        )

    news = News(
        author_id=user.id,
        title=title,
        content=content,
        status=status,
        published_at=utc_now() if status == "published" else None,
    )
    db.session.add(news)
    db.session.flush()
    log_operation(
        "news",
        "create",
        target_type="news",
        target_id=news.id,
        detail={"status": status},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(serialize_news(news), message="news created", status=201)


@news_bp.put("/<int:news_id>")
@roles_required("landlord", "admin")
def update_news(news_id):
    user = get_current_user()
    role = get_jwt().get("role")
    news, error = _get_news_or_404(news_id)
    if error:
        return error
    if not _can_manage_news(user, role, news):
        return error_response("permission denied", code=4003, status=403)

    payload = request.get_json(silent=True) or {}
    if "title" in payload:
        title = (payload.get("title") or "").strip()
        if not title:
            return error_response(
                "validation error",
                code=4001,
                errors={"title": ["title cannot be empty"]},
            )
        news.title = title

    if "content" in payload:
        content = (payload.get("content") or "").strip()
        if not content:
            return error_response(
                "validation error",
                code=4001,
                errors={"content": ["content cannot be empty"]},
            )
        news.content = content

    log_operation(
        "news",
        "update",
        target_type="news",
        target_id=news.id,
        detail={"fields": [field for field in ["title", "content"] if field in payload]},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(serialize_news(news), message="news updated")


@news_bp.patch("/<int:news_id>/status")
@roles_required("landlord", "admin")
def update_news_status(news_id):
    user = get_current_user()
    role = get_jwt().get("role")
    news, error = _get_news_or_404(news_id)
    if error:
        return error
    if not _can_manage_news(user, role, news):
        return error_response("permission denied", code=4003, status=403)

    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    if status not in {"draft", "published", "archived"}:
        return error_response(
            "validation error",
            code=4001,
            errors={"status": ["status must be draft, published, or archived"]},
        )

    news.status = status
    if status == "published" and news.published_at is None:
        news.published_at = utc_now()

    log_operation(
        "news",
        "update_status",
        target_type="news",
        target_id=news.id,
        detail={"status": status},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(serialize_news(news), message="news status updated")


@news_bp.delete("/<int:news_id>")
@roles_required("landlord", "admin")
def delete_news(news_id):
    user = get_current_user()
    role = get_jwt().get("role")
    news, error = _get_news_or_404(news_id)
    if error:
        return error
    if not _can_manage_news(user, role, news):
        return error_response("permission denied", code=4003, status=403)

    log_operation(
        "news",
        "delete",
        target_type="news",
        target_id=news.id,
        detail={"title": news.title},
        operator_id=user.id,
    )
    db.session.delete(news)
    db.session.commit()

    return success_response(message="news deleted")
