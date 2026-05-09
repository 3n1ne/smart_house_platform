def _to_float(value):
    return float(value) if value is not None else None


def serialize_payment(payment):
    return {
        "id": payment.id,
        "contract_id": payment.contract_id,
        "payer_id": payment.payer_id,
        "payee_id": payment.payee_id,
        "amount": _to_float(payment.amount),
        "payment_type": payment.payment_type,
        "payment_method": payment.payment_method,
        "transaction_no": payment.transaction_no,
        "due_date": payment.due_date.isoformat() if payment.due_date else None,
        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
        "status": payment.status,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
        "updated_at": payment.updated_at.isoformat() if payment.updated_at else None,
        "contract": {
            "id": payment.contract.id,
            "contract_no": payment.contract.contract_no,
            "status": payment.contract.status,
            "house": {
                "id": payment.contract.house.id,
                "title": payment.contract.house.title,
            }
            if payment.contract.house
            else None,
        }
        if payment.contract
        else None,
        "payer": {
            "id": payment.payer.id,
            "username": payment.payer.username,
            "real_name": payment.payer.real_name,
        }
        if payment.payer
        else None,
        "payee": {
            "id": payment.payee.id,
            "username": payment.payee.username,
            "real_name": payment.payee.real_name,
        }
        if payment.payee
        else None,
    }
