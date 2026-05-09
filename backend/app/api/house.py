import os
from uuid import uuid4

from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.base import utc_now
from app.models.house import House
from app.models.house_media import HouseMedia
from app.schemas.house import serialize_house
from app.utils.api_response import error_response, success_response
from app.utils.auth import get_current_user, roles_required
from app.utils.operation_log import log_operation


house_bp = Blueprint("house", __name__)
ALLOWED_MEDIA_EXTENSIONS = {
    "jpg": "image",
    "jpeg": "image",
    "png": "image",
    "gif": "image",
    "webp": "image",
    "mp4": "video",
    "webm": "video",
    "mov": "video",
}


def _get_house_or_404(house_id):
    house = db.session.get(House, house_id)
    if house is None:
        return None, error_response("resource not found", code=4004, status=404)
    return house, None


def _can_manage_house(user, role, house):
    return role == "admin" or (role == "landlord" and user and house.landlord_id == user.id)


def _media_type_from_filename(filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ALLOWED_MEDIA_EXTENSIONS.get(extension)


@house_bp.get("/mine")
@roles_required("landlord", "admin")
def list_my_houses():
    user = get_current_user()
    role = get_jwt().get("role")

    query = House.query
    if role == "landlord":
        query = query.filter(House.landlord_id == user.id)

    status = request.args.get("status")
    keyword = request.args.get("keyword")
    city = request.args.get("city")

    if status:
        query = query.filter(House.status == status)
    if city:
        query = query.filter(House.city == city)
    if keyword:
        like_value = f"%{keyword}%"
        query = query.filter(
            or_(
                House.title.like(like_value),
                House.community.like(like_value),
                House.address_detail.like(like_value),
            )
        )

    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 50)
    pagination = query.order_by(House.id.desc()).paginate(page=page, per_page=page_size)

    return success_response(
        {
            "items": [
                serialize_house(house, include_media=True, include_landlord=True)
                for house in pagination.items
            ],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": pagination.total,
            },
        }
    )


@house_bp.post("")
@roles_required("landlord")
def create_house():
    user = get_current_user()
    payload = request.get_json(silent=True) or {}

    required_fields = ["title", "city", "district", "address_detail", "layout", "area", "rent"]
    missing_fields = [field for field in required_fields if payload.get(field) in (None, "")]
    if missing_fields:
        return error_response(
            "validation error",
            code=4001,
            errors={"missing_fields": missing_fields},
        )

    house = House(
        landlord_id=user.id,
        title=payload["title"],
        province=payload.get("province"),
        city=payload["city"],
        district=payload["district"],
        community=payload.get("community"),
        address_detail=payload["address_detail"],
        house_type=payload.get("house_type"),
        layout=payload["layout"],
        area=payload["area"],
        rent=payload["rent"],
        deposit=payload.get("deposit", 0),
        decoration=payload.get("decoration"),
        floor=payload.get("floor"),
        total_floors=payload.get("total_floors"),
        orientation=payload.get("orientation"),
        description=payload.get("description"),
        status=payload.get("status", "draft"),
        published_at=utc_now() if payload.get("status") == "available" else None,
    )
    db.session.add(house)
    db.session.flush()
    log_operation(
        "house",
        "create",
        target_type="house",
        target_id=house.id,
        detail={"title": house.title, "status": house.status},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(
        serialize_house(house, include_landlord=True),
        message="house created",
        status=201,
    )


@house_bp.get("")
def list_houses():
    query = House.query.filter(House.status == "available")

    filters = {
        "city": request.args.get("city"),
        "district": request.args.get("district"),
        "layout": request.args.get("layout"),
    }
    for field, value in filters.items():
        if value:
            query = query.filter(getattr(House, field) == value)

    keyword = request.args.get("keyword")
    if keyword:
        like_value = f"%{keyword}%"
        query = query.filter(
            or_(
                House.title.like(like_value),
                House.community.like(like_value),
                House.address_detail.like(like_value),
            )
        )

    min_rent = request.args.get("min_rent")
    max_rent = request.args.get("max_rent")
    if min_rent:
        query = query.filter(House.rent >= min_rent)
    if max_rent:
        query = query.filter(House.rent <= max_rent)

    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 10)), 1), 50)
    pagination = query.order_by(House.id.desc()).paginate(page=page, per_page=page_size)

    return success_response(
        {
            "items": [serialize_house(house) for house in pagination.items],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": pagination.total,
            },
        }
    )


@house_bp.get("/<int:house_id>")
def get_house_detail(house_id):
    house, error = _get_house_or_404(house_id)
    if error:
        return error

    verify_jwt_in_request(optional=True)
    identity = get_jwt_identity()
    claims = get_jwt() if identity else {}
    role = claims.get("role")
    can_view_private = identity and (
        role == "admin" or (role == "landlord" and int(identity) == house.landlord_id)
    )

    if house.status != "available" and not can_view_private:
        return error_response("resource not found", code=4004, status=404)

    return success_response(serialize_house(house, include_media=True, include_landlord=True))


@house_bp.put("/<int:house_id>")
@roles_required("landlord", "admin")
def update_house(house_id):
    house, error = _get_house_or_404(house_id)
    if error:
        return error

    user = get_current_user()
    claims = get_jwt()
    role = claims.get("role")

    if not _can_manage_house(user, role, house):
        return error_response("permission denied", code=4003, status=403)

    payload = request.get_json(silent=True) or {}
    editable_fields = [
        "title",
        "province",
        "city",
        "district",
        "community",
        "address_detail",
        "house_type",
        "layout",
        "area",
        "rent",
        "deposit",
        "decoration",
        "floor",
        "total_floors",
        "orientation",
        "description",
    ]

    for field in editable_fields:
        if field in payload:
            setattr(house, field, payload[field])

    log_operation(
        "house",
        "update",
        target_type="house",
        target_id=house.id,
        detail={"fields": [field for field in editable_fields if field in payload]},
        operator_id=user.id if user else None,
    )
    db.session.commit()
    return success_response(
        serialize_house(house, include_media=True, include_landlord=True),
        message="house updated",
    )


@house_bp.delete("/<int:house_id>")
@roles_required("landlord", "admin")
def delete_house(house_id):
    house, error = _get_house_or_404(house_id)
    if error:
        return error

    user = get_current_user()
    role = get_jwt().get("role")
    if not _can_manage_house(user, role, house):
        return error_response("permission denied", code=4003, status=403)

    house.status = "offline"
    log_operation(
        "house",
        "offline",
        target_type="house",
        target_id=house.id,
        operator_id=user.id if user else None,
    )
    db.session.commit()
    return success_response(message="house offline success")


@house_bp.patch("/<int:house_id>/status")
@roles_required("landlord", "admin")
def update_house_status(house_id):
    house, error = _get_house_or_404(house_id)
    if error:
        return error

    user = get_current_user()
    role = get_jwt().get("role")
    if not _can_manage_house(user, role, house):
        return error_response("permission denied", code=4003, status=403)

    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    allowed_statuses = {"draft", "available", "rented", "repairing", "offline"}
    if status not in allowed_statuses:
        return error_response(
            "validation error",
            code=4001,
            errors={"status": [f"status must be one of {sorted(allowed_statuses)}"]},
        )

    house.status = status
    if status == "available" and house.published_at is None:
        house.published_at = utc_now()
    log_operation(
        "house",
        "update_status",
        target_type="house",
        target_id=house.id,
        detail={"status": status},
        operator_id=user.id if user else None,
    )
    db.session.commit()

    return success_response(serialize_house(house), message="house status updated")


@house_bp.post("/<int:house_id>/media")
@roles_required("landlord", "admin")
def add_house_media(house_id):
    house, error = _get_house_or_404(house_id)
    if error:
        return error

    user = get_current_user()
    role = get_jwt().get("role")
    if not _can_manage_house(user, role, house):
        return error_response("permission denied", code=4003, status=403)

    payload = request.get_json(silent=True) or {}
    media_type = payload.get("media_type")
    file_url = payload.get("file_url")
    sort_order = payload.get("sort_order", 0)

    upload = request.files.get("file")
    if upload and upload.filename:
        original_name = secure_filename(upload.filename)
        media_type = _media_type_from_filename(original_name)
        if media_type is None:
            return error_response(
                "validation error",
                code=4001,
                errors={"file": ["only image or video files are allowed"]},
            )

        extension = original_name.rsplit(".", 1)[-1].lower()
        filename = f"{uuid4().hex}.{extension}"
        relative_dir = os.path.join("houses", str(house.id))
        upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], relative_dir)
        os.makedirs(upload_dir, exist_ok=True)
        upload.save(os.path.join(upload_dir, filename))
        file_url = f"/uploads/houses/{house.id}/{filename}"
        sort_order = request.form.get("sort_order", sort_order)

    if media_type not in {"image", "video"} or not file_url:
        return error_response(
            "validation error",
            code=4001,
            errors={"media": ["media_type must be image or video and file_url is required"]},
        )

    media = HouseMedia(
        house_id=house.id,
        media_type=media_type,
        file_url=file_url,
        sort_order=int(sort_order or 0),
    )
    db.session.add(media)
    db.session.flush()
    log_operation(
        "house",
        "add_media",
        target_type="house_media",
        target_id=media.id,
        detail={"house_id": house.id, "media_type": media.media_type},
        operator_id=user.id if user else None,
    )
    db.session.commit()

    return success_response(
        serialize_house(house, include_media=True, include_landlord=True),
        message="house media added",
        status=201,
    )


@house_bp.delete("/<int:house_id>/media/<int:media_id>")
@roles_required("landlord", "admin")
def delete_house_media(house_id, media_id):
    house, error = _get_house_or_404(house_id)
    if error:
        return error

    user = get_current_user()
    role = get_jwt().get("role")
    if not _can_manage_house(user, role, house):
        return error_response("permission denied", code=4003, status=403)

    media = db.session.get(HouseMedia, media_id)
    if media is None or media.house_id != house.id:
        return error_response("resource not found", code=4004, status=404)

    file_url = media.file_url or ""
    if file_url.startswith("/uploads/"):
        relative_path = file_url.removeprefix("/uploads/").replace("/", os.sep)
        upload_root = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
        file_path = os.path.abspath(os.path.join(upload_root, relative_path))
        if file_path.startswith(upload_root) and os.path.exists(file_path):
            os.remove(file_path)

    log_operation(
        "house",
        "delete_media",
        target_type="house_media",
        target_id=media.id,
        detail={"house_id": house.id, "file_url": file_url},
        operator_id=user.id if user else None,
    )
    db.session.delete(media)
    db.session.commit()

    return success_response(
        serialize_house(house, include_media=True, include_landlord=True),
        message="house media deleted",
    )
