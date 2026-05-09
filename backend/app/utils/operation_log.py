import json

from flask import has_request_context, request

from app.extensions import db
from app.models.operation_log import OperationLog


def log_operation(module, action, target_type=None, target_id=None, detail=None, operator_id=None):
    ip_address = None
    user_agent = None
    if has_request_context():
        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
        if ip_address and "," in ip_address:
            ip_address = ip_address.split(",", 1)[0].strip()
        user_agent = request.headers.get("User-Agent")

    if detail is not None and not isinstance(detail, str):
        detail = json.dumps(detail, ensure_ascii=False, default=str)

    db.session.add(
        OperationLog(
            operator_id=operator_id,
            module=module,
            action=action,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent[:255] if user_agent else None,
            detail=detail,
        )
    )
