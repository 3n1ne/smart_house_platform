from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from app.extensions import db
from app.models.base import utc_now
from app.models.complaint import Complaint
from app.models.house import House
from app.schemas.complaint import serialize_complaint
from app.utils.api_response import error_response, success_response
from app.utils.auth import get_current_user, roles_required
from app.utils.operation_log import log_operation


complaint_bp = Blueprint("complaint", __name__)


def _get_complaint_or_404(complaint_id):
    complaint = db.session.get(Complaint, complaint_id)
    if complaint is None:
        return None, error_response("resource not found", code=4004, status=404)
    return complaint, None


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 50)
    pagination = query.paginate(page=page, per_page=page_size)
    return success_response(
        {
            "items": [serialize_complaint(item) for item in pagination.items],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": pagination.total,
            },
        }
    )


@complaint_bp.post("")
@roles_required("tenant", "landlord")
def create_complaint():
    user = get_current_user()
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    content = (payload.get("content") or "").strip()
    house_id = payload.get("house_id")

    if not title or not content:
        return error_response(
            "validation error",
            code=4001,
            errors={"complaint": ["title and content are required"]},
        )

    if house_id and db.session.get(House, int(house_id)) is None:
        return error_response("resource not found", code=4004, status=404)

    complaint = Complaint(
        house_id=int(house_id) if house_id else None,
        complainant_id=user.id,
        title=title,
        content=content,
        status="submitted",
    )
    db.session.add(complaint)
    db.session.flush()
    log_operation(
        "complaint",
        "create",
        target_type="complaint",
        target_id=complaint.id,
        detail={"house_id": complaint.house_id},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(
        serialize_complaint(complaint),
        message="complaint submitted",
        status=201,
    )


@complaint_bp.get("/mine")
@roles_required("tenant", "landlord", "admin")
def list_my_complaints():
    user = get_current_user()
    role = get_jwt().get("role")
    query = Complaint.query

    if role != "admin":
        query = query.filter(Complaint.complainant_id == user.id)

    status = request.args.get("status")
    house_id = request.args.get("house_id")
    if status:
        query = query.filter(Complaint.status == status)
    if house_id:
        query = query.filter(Complaint.house_id == int(house_id))

    return _paginate(query.order_by(Complaint.created_at.desc()))


@complaint_bp.patch("/<int:complaint_id>/status")
@roles_required("admin")
def update_complaint_status(complaint_id):
    user = get_current_user()
    complaint, error = _get_complaint_or_404(complaint_id)
    if error:
        return error

    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    allowed_statuses = {"submitted", "processing", "resolved", "rejected"}
    if status not in allowed_statuses:
        return error_response(
            "validation error",
            code=4001,
            errors={"status": [f"status must be one of {sorted(allowed_statuses)}"]},
        )

    complaint.status = status
    complaint.result = payload.get("result", complaint.result)
    complaint.handler_id = user.id
    if status in {"processing", "resolved", "rejected"}:
        complaint.handled_at = utc_now()

    log_operation(
        "complaint",
        "update_status",
        target_type="complaint",
        target_id=complaint.id,
        detail={"status": status},
        operator_id=user.id,
    )
    db.session.commit()
    return success_response(
        serialize_complaint(complaint),
        message="complaint status updated",
    )
