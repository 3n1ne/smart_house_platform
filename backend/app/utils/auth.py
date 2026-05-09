from functools import wraps

from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from app.extensions import db
from app.models.user import User
from app.utils.api_response import error_response


def get_current_user():
    identity = get_jwt_identity()
    if identity is None:
        return None
    return db.session.get(User, int(identity))


def roles_required(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")

            if role not in allowed_roles:
                return error_response("permission denied", code=4003, status=403)

            return func(*args, **kwargs)

        return wrapper

    return decorator
