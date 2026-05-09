from app.extensions import db
from app.models.role import Role


DEFAULT_ROLES = [
    {"code": "admin", "name": "Administrator", "description": "System administrator"},
    {"code": "landlord", "name": "Landlord", "description": "House owner"},
    {"code": "tenant", "name": "Tenant", "description": "House renter"},
]


def seed_roles():
    existing_codes = {role.code for role in Role.query.all()}
    missing_roles = [
        Role(**role_data)
        for role_data in DEFAULT_ROLES
        if role_data["code"] not in existing_codes
    ]

    if not missing_roles:
        return

    db.session.add_all(missing_roles)
    db.session.commit()
