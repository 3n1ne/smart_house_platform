from app.utils.sensitive import mask_email, mask_identity_no, mask_phone


def serialize_user(user, include_private=False):
    email = user.email if include_private else mask_email(user.email)
    phone = user.phone if include_private else mask_phone(user.phone)

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.code if user.role else None,
        "email": email,
        "phone": phone,
        "real_name": user.real_name,
        "avatar_url": user.avatar_url,
        "gender": user.gender,
        "identity_no_masked": mask_identity_no(user.identity_no),
        "status": user.status,
        "is_mfa_enabled": user.is_mfa_enabled,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }
