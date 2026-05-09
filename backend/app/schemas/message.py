def serialize_message_user(user):
    if user is None:
        return None

    return {
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "phone": user.phone,
        "role": user.role.code if user.role else None,
    }


def serialize_message_house(house):
    if house is None:
        return None

    return {
        "id": house.id,
        "title": house.title,
        "city": house.city,
        "district": house.district,
        "community": house.community,
        "address_detail": house.address_detail,
    }


def serialize_message(message, current_user_id=None):
    return {
        "id": message.id,
        "sender_id": message.sender_id,
        "receiver_id": message.receiver_id,
        "house_id": message.house_id,
        "content": message.content,
        "is_read": message.is_read,
        "is_mine": current_user_id == message.sender_id if current_user_id is not None else None,
        "created_at": message.created_at.isoformat() if message.created_at else None,
        "updated_at": message.updated_at.isoformat() if message.updated_at else None,
        "sender": serialize_message_user(message.sender),
        "receiver": serialize_message_user(message.receiver),
        "house": serialize_message_house(message.house),
    }


def serialize_message_conversation(summary, current_user_id):
    last_message = summary["last_message"]

    return {
        "conversation_key": summary["conversation_key"],
        "unread_count": summary["unread_count"],
        "message_count": summary["message_count"],
        "last_message_at": last_message.created_at.isoformat() if last_message.created_at else None,
        "counterpart": serialize_message_user(summary["counterpart"]),
        "house": serialize_message_house(summary["house"]),
        "last_message": {
            "id": last_message.id,
            "content": last_message.content,
            "created_at": last_message.created_at.isoformat() if last_message.created_at else None,
            "sender_id": last_message.sender_id,
            "is_mine": last_message.sender_id == current_user_id,
            "is_read": last_message.is_read,
        },
    }
