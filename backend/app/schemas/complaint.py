def serialize_complaint(complaint):
    return {
        "id": complaint.id,
        "house_id": complaint.house_id,
        "complainant_id": complaint.complainant_id,
        "handler_id": complaint.handler_id,
        "title": complaint.title,
        "content": complaint.content,
        "status": complaint.status,
        "result": complaint.result,
        "handled_at": complaint.handled_at.isoformat() if complaint.handled_at else None,
        "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
        "updated_at": complaint.updated_at.isoformat() if complaint.updated_at else None,
        "house": {
            "id": complaint.house.id,
            "title": complaint.house.title,
            "city": complaint.house.city,
            "district": complaint.house.district,
            "community": complaint.house.community,
            "address_detail": complaint.house.address_detail,
        }
        if complaint.house
        else None,
        "complainant": {
            "id": complaint.complainant.id,
            "username": complaint.complainant.username,
            "real_name": complaint.complainant.real_name,
            "phone": complaint.complainant.phone,
        }
        if complaint.complainant
        else None,
        "handler": {
            "id": complaint.handler.id,
            "username": complaint.handler.username,
            "real_name": complaint.handler.real_name,
        }
        if complaint.handler
        else None,
    }
