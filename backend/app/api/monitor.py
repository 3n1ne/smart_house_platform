from flask import Blueprint

from app.models.base import utc_now
from app.models.operation_log import OperationLog
from app.utils.api_response import success_response
from app.utils.auth import roles_required


monitor_bp = Blueprint("monitor", __name__)


def _serialize_log(log):
    return {
        "id": log.id,
        "operator_id": log.operator_id,
        "module": log.module,
        "action": log.action,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "detail": log.detail,
        "created_at": log.created_at.isoformat() if log.created_at else None,
        "operator": {
            "id": log.operator.id,
            "username": log.operator.username,
            "real_name": log.operator.real_name,
        }
        if log.operator
        else None,
    }


@monitor_bp.get("/overview")
@roles_required("admin")
def overview():
    recent_logs = OperationLog.query.order_by(OperationLog.created_at.desc()).limit(10).all()
    return success_response(
        {
            "service": "backend",
            "status": "ok",
            "checked_at": utc_now().isoformat(),
            "modules": {
                "auth": "ok",
                "house": "ok",
                "booking": "ok",
                "contract": "ok",
                "payment": "ok",
                "message": "ok",
                "repair": "ok",
                "complaint": "ok",
                "news": "ok",
                "report": "ok",
            },
            "recent_logs": [_serialize_log(log) for log in recent_logs],
        }
    )
