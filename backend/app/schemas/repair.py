def serialize_repair(repair):
    return {
        "id": repair.id,
        "house_id": repair.house_id,
        "tenant_id": repair.tenant_id,
        "handler_id": repair.handler_id,
        "title": repair.title,
        "description": repair.description,
        "priority": repair.priority,
        "status": repair.status,
        "handled_at": repair.handled_at.isoformat() if repair.handled_at else None,
        "completed_at": repair.completed_at.isoformat() if repair.completed_at else None,
        "created_at": repair.created_at.isoformat() if repair.created_at else None,
        "updated_at": repair.updated_at.isoformat() if repair.updated_at else None,
        "house": {
            "id": repair.house.id,
            "title": repair.house.title,
            "city": repair.house.city,
            "district": repair.house.district,
            "community": repair.house.community,
            "address_detail": repair.house.address_detail,
        }
        if repair.house
        else None,
        "tenant": {
            "id": repair.tenant.id,
            "username": repair.tenant.username,
            "real_name": repair.tenant.real_name,
            "phone": repair.tenant.phone,
        }
        if repair.tenant
        else None,
        "handler": {
            "id": repair.handler.id,
            "username": repair.handler.username,
            "real_name": repair.handler.real_name,
        }
        if repair.handler
        else None,
    }
