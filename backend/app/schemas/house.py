def _to_float(value):
    return float(value) if value is not None else None


def serialize_house_media(media):
    return {
        "id": media.id,
        "media_type": media.media_type,
        "file_url": media.file_url,
        "sort_order": media.sort_order,
    }


def serialize_house(house, include_media=False, include_landlord=False):
    media_items = sorted(house.media_items, key=lambda item: item.sort_order)
    cover_url = media_items[0].file_url if media_items else None

    data = {
        "id": house.id,
        "landlord_id": house.landlord_id,
        "title": house.title,
        "province": house.province,
        "city": house.city,
        "district": house.district,
        "community": house.community,
        "address_detail": house.address_detail,
        "house_type": house.house_type,
        "layout": house.layout,
        "area": _to_float(house.area),
        "rent": _to_float(house.rent),
        "deposit": _to_float(house.deposit),
        "decoration": house.decoration,
        "floor": house.floor,
        "total_floors": house.total_floors,
        "orientation": house.orientation,
        "description": house.description,
        "status": house.status,
        "cover_url": cover_url,
        "published_at": house.published_at.isoformat() if house.published_at else None,
        "created_at": house.created_at.isoformat() if house.created_at else None,
        "updated_at": house.updated_at.isoformat() if house.updated_at else None,
    }

    if include_media:
        data["media_items"] = [serialize_house_media(item) for item in media_items]

    if include_landlord and house.landlord:
        data["landlord"] = {
            "id": house.landlord.id,
            "username": house.landlord.username,
            "real_name": house.landlord.real_name,
            "phone": house.landlord.phone,
        }

    return data
