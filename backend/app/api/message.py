from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.house import House
from app.models.message import Message
from app.models.user import User
from app.schemas.message import serialize_message, serialize_message_conversation
from app.utils.api_response import error_response, success_response
from app.utils.auth import get_current_user
from app.utils.operation_log import log_operation


message_bp = Blueprint("message", __name__)


def _parse_int(value, field_name):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be an integer")


def _parse_optional_house_id(source, field_name="house_id"):
    if field_name not in source:
        return False, None

    value = source.get(field_name)
    if value in (None, "", "null"):
        return True, None

    return True, _parse_int(value, field_name)


def _base_message_query():
    return Message.query.options(
        joinedload(Message.sender).joinedload(User.role),
        joinedload(Message.receiver).joinedload(User.role),
        joinedload(Message.house),
    )


@message_bp.get("/conversations")
@jwt_required()
def list_conversations():
    user = get_current_user()
    if user is None:
        return error_response("resource not found", code=4004, status=404)

    messages = (
        _base_message_query()
        .filter(or_(Message.sender_id == user.id, Message.receiver_id == user.id))
        .order_by(Message.created_at.desc(), Message.id.desc())
        .all()
    )

    summaries = {}
    unread_total = 0
    for message in messages:
        counterpart = message.receiver if message.sender_id == user.id else message.sender
        if counterpart is None:
            continue

        conversation_key = f"{message.house_id or 0}:{counterpart.id}"
        summary = summaries.get(conversation_key)
        if summary is None:
            summary = {
                "conversation_key": conversation_key,
                "counterpart": counterpart,
                "house": message.house,
                "last_message": message,
                "unread_count": 0,
                "message_count": 0,
            }
            summaries[conversation_key] = summary

        summary["message_count"] += 1
        if message.receiver_id == user.id and not message.is_read:
            summary["unread_count"] += 1
            unread_total += 1

    items = [
        serialize_message_conversation(summary, user.id) for summary in summaries.values()
    ]

    return success_response(
        {
            "items": items,
            "unread_total": unread_total,
        }
    )


@message_bp.get("")
@jwt_required()
def list_messages():
    user = get_current_user()
    if user is None:
        return error_response("resource not found", code=4004, status=404)

    counterpart_id = request.args.get("counterpart_id")
    if not counterpart_id:
        return error_response(
            "validation error",
            code=4001,
            errors={"counterpart_id": ["counterpart_id is required"]},
        )

    try:
        counterpart_id = _parse_int(counterpart_id, "counterpart_id")
        house_id_provided, house_id = _parse_optional_house_id(request.args)
    except ValueError as exc:
        return error_response(
            "validation error",
            code=4001,
            errors={"query": [str(exc)]},
        )

    counterpart = db.session.get(User, counterpart_id)
    if counterpart is None:
        return error_response("resource not found", code=4004, status=404)

    query = _base_message_query().filter(
        or_(
            and_(Message.sender_id == user.id, Message.receiver_id == counterpart_id),
            and_(Message.sender_id == counterpart_id, Message.receiver_id == user.id),
        )
    )

    if house_id_provided:
        if house_id is None:
            query = query.filter(Message.house_id.is_(None))
        else:
            query = query.filter(Message.house_id == house_id)

    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 50)), 1), 100)
    pagination = query.order_by(Message.created_at.asc(), Message.id.asc()).paginate(
        page=page,
        per_page=page_size,
    )

    unread_query = Message.query.filter(
        Message.sender_id == counterpart_id,
        Message.receiver_id == user.id,
        Message.is_read.is_(False),
    )
    if house_id_provided:
        if house_id is None:
            unread_query = unread_query.filter(Message.house_id.is_(None))
        else:
            unread_query = unread_query.filter(Message.house_id == house_id)

    return success_response(
        {
            "items": [
                serialize_message(message, current_user_id=user.id)
                for message in pagination.items
            ],
            "counterpart": {
                "id": counterpart.id,
                "username": counterpart.username,
                "real_name": counterpart.real_name,
                "phone": counterpart.phone,
                "role": counterpart.role.code if counterpart.role else None,
            },
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": pagination.total,
            },
            "unread_count": unread_query.count(),
        }
    )


@message_bp.post("")
@jwt_required()
def create_message():
    user = get_current_user()
    if user is None:
        return error_response("resource not found", code=4004, status=404)

    payload = request.get_json(silent=True) or {}
    receiver_id = payload.get("receiver_id")
    content = (payload.get("content") or "").strip()

    if not receiver_id or not content:
        return error_response(
            "validation error",
            code=4001,
            errors={"message": ["receiver_id and content are required"]},
        )

    try:
        receiver_id = _parse_int(receiver_id, "receiver_id")
        _, house_id = _parse_optional_house_id(payload)
    except ValueError as exc:
        return error_response(
            "validation error",
            code=4001,
            errors={"message": [str(exc)]},
        )

    if receiver_id == user.id:
        return error_response(
            "validation error",
            code=4001,
            errors={"receiver_id": ["cannot send a message to yourself"]},
        )

    receiver = db.session.get(User, receiver_id)
    if receiver is None:
        return error_response("resource not found", code=4004, status=404)

    house = None
    if house_id is not None:
        house = db.session.get(House, house_id)
        if house is None:
            return error_response("resource not found", code=4004, status=404)
        if house.landlord_id not in {user.id, receiver.id}:
            return error_response(
                "validation error",
                code=4001,
                errors={
                    "house_id": [
                        "house conversations must involve the landlord of the selected house"
                    ]
                },
            )

    message = Message(
        sender_id=user.id,
        receiver_id=receiver.id,
        house_id=house.id if house else None,
        content=content,
        is_read=False,
    )
    db.session.add(message)
    db.session.flush()
    log_operation(
        "message",
        "send",
        target_type="message",
        target_id=message.id,
        detail={"receiver_id": receiver.id, "house_id": message.house_id},
        operator_id=user.id,
    )
    db.session.commit()

    return success_response(
        serialize_message(message, current_user_id=user.id),
        message="message sent",
        status=201,
    )


@message_bp.patch("/read")
@jwt_required()
def mark_messages_read():
    user = get_current_user()
    if user is None:
        return error_response("resource not found", code=4004, status=404)

    payload = request.get_json(silent=True) or {}
    counterpart_id = payload.get("counterpart_id")
    if not counterpart_id:
        return error_response(
            "validation error",
            code=4001,
            errors={"counterpart_id": ["counterpart_id is required"]},
        )

    try:
        counterpart_id = _parse_int(counterpart_id, "counterpart_id")
        house_id_provided, house_id = _parse_optional_house_id(payload)
    except ValueError as exc:
        return error_response(
            "validation error",
            code=4001,
            errors={"message": [str(exc)]},
        )

    query = Message.query.filter(
        Message.sender_id == counterpart_id,
        Message.receiver_id == user.id,
        Message.is_read.is_(False),
    )

    if house_id_provided:
        if house_id is None:
            query = query.filter(Message.house_id.is_(None))
        else:
            query = query.filter(Message.house_id == house_id)

    unread_messages = query.all()
    for message in unread_messages:
        message.is_read = True

    db.session.commit()

    unread_total = (
        Message.query.filter(
            Message.receiver_id == user.id,
            Message.is_read.is_(False),
        ).count()
    )

    return success_response(
        {
            "updated": len(unread_messages),
            "unread_total": unread_total,
        },
        message="messages marked as read",
    )
