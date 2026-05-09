def serialize_booking(booking):
    return {
        "id": booking.id,
        "house_id": booking.house_id,
        "tenant_id": booking.tenant_id,
        "landlord_id": booking.landlord_id,
        "appointment_time": (
            booking.appointment_time.isoformat() if booking.appointment_time else None
        ),
        "status": booking.status,
        "remark": booking.remark,
        "confirmed_at": booking.confirmed_at.isoformat() if booking.confirmed_at else None,
        "created_at": booking.created_at.isoformat() if booking.created_at else None,
        "updated_at": booking.updated_at.isoformat() if booking.updated_at else None,
        "house": {
            "id": booking.house.id,
            "title": booking.house.title,
            "city": booking.house.city,
            "district": booking.house.district,
            "community": booking.house.community,
            "address_detail": booking.house.address_detail,
            "layout": booking.house.layout,
            "rent": float(booking.house.rent) if booking.house.rent is not None else None,
        }
        if booking.house
        else None,
        "tenant": {
            "id": booking.tenant.id,
            "username": booking.tenant.username,
            "real_name": booking.tenant.real_name,
            "phone": booking.tenant.phone,
        }
        if booking.tenant
        else None,
        "landlord": {
            "id": booking.landlord.id,
            "username": booking.landlord.username,
            "real_name": booking.landlord.real_name,
            "phone": booking.landlord.phone,
        }
        if booking.landlord
        else None,
    }
