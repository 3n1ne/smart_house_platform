def serialize_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.code if user.role else None,
        "email": user.email,
        "phone": user.phone,
        "real_name": user.real_name,
        "avatar_url": user.avatar_url,
        "gender": user.gender,
        "status": user.status,
        "is_mfa_enabled": user.is_mfa_enabled,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }
