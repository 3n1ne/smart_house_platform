def _to_float(value):
    return float(value) if value is not None else None


def serialize_contract(contract):
    return {
        "id": contract.id,
        "contract_no": contract.contract_no,
        "house_id": contract.house_id,
        "landlord_id": contract.landlord_id,
        "tenant_id": contract.tenant_id,
        "start_date": contract.start_date.isoformat() if contract.start_date else None,
        "end_date": contract.end_date.isoformat() if contract.end_date else None,
        "monthly_rent": _to_float(contract.monthly_rent),
        "deposit": _to_float(contract.deposit),
        "payment_cycle": contract.payment_cycle,
        "status": contract.status,
        "signed_at": contract.signed_at.isoformat() if contract.signed_at else None,
        "content": contract.content,
        "created_at": contract.created_at.isoformat() if contract.created_at else None,
        "updated_at": contract.updated_at.isoformat() if contract.updated_at else None,
        "house": {
            "id": contract.house.id,
            "title": contract.house.title,
            "city": contract.house.city,
            "district": contract.house.district,
            "community": contract.house.community,
            "address_detail": contract.house.address_detail,
            "layout": contract.house.layout,
        }
        if contract.house
        else None,
        "tenant": {
            "id": contract.tenant.id,
            "username": contract.tenant.username,
            "real_name": contract.tenant.real_name,
            "phone": contract.tenant.phone,
        }
        if contract.tenant
        else None,
        "landlord": {
            "id": contract.landlord.id,
            "username": contract.landlord.username,
            "real_name": contract.landlord.real_name,
            "phone": contract.landlord.phone,
        }
        if contract.landlord
        else None,
    }
