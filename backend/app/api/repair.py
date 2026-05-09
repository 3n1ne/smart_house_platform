from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from app.extensions import db
from app.models.base import utc_now
from app.models.contract import Contract
from app.models.house import House
from app.models.repair import Repair
from app.schemas.repair import serialize_repair
from app.utils.api_response import error_response, success_response
from app.utils.auth import get_current_user, roles_required
from app.utils.operation_log import log_operation


repair_bp = Blueprint("repair", __name__)


def _get_repair_or_404(repair_id):
    repair = db.session.get(Repair, repair_id)
    if repair is None:
        return None, error_response("resource not found", code=4004, status=404)
    return repair, None


def _paginate(query, serializer):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 50)
    pagination = query.paginate(page=page, per_page=page_size)
    return success_response(
        {
            "items": [serializer(item) for item in pagination.items],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": pagination.total,
            },
        }
    )


@repair_bp.post("")
@roles_required("tenant")
def create_repair():
    user = get_current_user()
    payload = request.get_json(silent=True) or {}
    house_id = payload.get("house_id")
    title = (payload.get("title") or "").strip()
    description = (payload.get("description") or "").strip()
    priority = payload.get("priority") or "medium"

    if not house_id or not title or not description:
        return error_response(
            "validation error",
            code=4001,
            errors={"repair": ["house_id, title and description are required"]},
        )
    if priority not in {"low", "medium", "high", "urgent"}:
        return error_response(
            "validation error",
            code=4001,
            errors={"priority": ["priority must be one of low, medium, high, urgent"]},
        )

    house = db.session.get(House, int(house_id))
    if house is None:
        return error_response("resource not found", code=4004, status=404)

    active_contract = Contract.query.filter(
        Contract.house_id == house.id,
        Contract.tenant_id == user.id,
        Contract.status == "active",
    ).first()
    if active_contract is None:
        return error_response("permission denied", code=4003, status=403)

    repair = Repair(
        house_id=house.id,
        tenant_id=user.id,
        title=title,
        description=description,
        priority=priority,
        status="submitted",
    )
    db.session.add(repair)
    db.session.flush()
    log_operation(
        "repair",
        "create",
        target_type="repair",
        target_id=repair.id,
        detail={"house_id": house.id, "priority": priority},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(serialize_repair(repair), message="repair submitted", status=201)


@repair_bp.get("/mine")
@roles_required("tenant", "landlord", "admin")
def list_my_repairs():
    user = get_current_user()
    role = get_jwt().get("role")
    query = Repair.query

    if role == "tenant":
        query = query.filter(Repair.tenant_id == user.id)
    elif role == "landlord":
        query = query.join(House, Repair.house_id == House.id).filter(House.landlord_id == user.id)

    status = request.args.get("status")
    house_id = request.args.get("house_id")
    priority = request.args.get("priority")
    if status:
        query = query.filter(Repair.status == status)
    if house_id:
        query = query.filter(Repair.house_id == int(house_id))
    if priority:
        query = query.filter(Repair.priority == priority)

    return _paginate(query.order_by(Repair.created_at.desc()), serialize_repair)


@repair_bp.patch("/<int:repair_id>/status")
@roles_required("landlord", "admin")
def update_repair_status(repair_id):
    user = get_current_user()
    role = get_jwt().get("role")
    repair, error = _get_repair_or_404(repair_id)
    if error:
        return error

    if role == "landlord" and repair.house.landlord_id != user.id:
        return error_response("permission denied", code=4003, status=403)

    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    allowed_statuses = {"submitted", "processing", "completed", "rejected"}
    if status not in allowed_statuses:
        return error_response(
            "validation error",
            code=4001,
            errors={"status": [f"status must be one of {sorted(allowed_statuses)}"]},
        )

    repair.status = status
    repair.handler_id = user.id
    if status in {"processing", "completed", "rejected"} and repair.handled_at is None:
        repair.handled_at = utc_now()
    if status == "completed":
        repair.completed_at = utc_now()
    else:
        repair.completed_at = None

    log_operation(
        "repair",
        "update_status",
        target_type="repair",
        target_id=repair.id,
        detail={"status": status},
        operator_id=user.id,
    )
    db.session.commit()
    return success_response(serialize_repair(repair), message="repair status updated")
