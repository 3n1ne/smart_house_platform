from datetime import timedelta

from app.extensions import db
from app.models.base import utc_now
from app.models.payment import Payment
from tests.conftest import login_user, register_user


def _create_signed_contract_payments(client):
    register_user(client, "payment_landlord", role="landlord")
    register_user(client, "payment_tenant", role="tenant")
    landlord_headers = login_user(client, "payment_landlord")
    tenant_headers = login_user(client, "payment_tenant")

    house = client.post(
        "/api/houses",
        json={
            "title": "Payment house",
            "city": "Hangzhou",
            "district": "Xihu",
            "address_detail": "No. 10",
            "layout": "2R1L",
            "area": 90,
            "rent": 5000,
            "deposit": 5000,
            "status": "available",
        },
        headers=landlord_headers,
    ).get_json()["data"]

    booking = client.post(
        "/api/bookings",
        json={
            "house_id": house["id"],
            "appointment_time": (utc_now() + timedelta(days=1)).isoformat(),
        },
        headers=tenant_headers,
    ).get_json()["data"]

    client.patch(
        f"/api/bookings/{booking['id']}/status",
        json={"status": "confirmed"},
        headers=landlord_headers,
    )

    contract = client.post(
        "/api/contracts",
        json={
            "booking_id": booking["id"],
            "start_date": "2026-06-01",
            "end_date": "2027-06-01",
            "payment_cycle": "monthly",
        },
        headers=landlord_headers,
    ).get_json()["data"]

    client.patch(f"/api/contracts/{contract['id']}/sign", headers=tenant_headers)
    payments = client.get("/api/payments/mine", headers=tenant_headers).get_json()["data"]["items"]
    return landlord_headers, tenant_headers, payments


def test_payment_can_be_paid_refunded_marked_overdue_and_failed(client, app):
    landlord_headers, tenant_headers, payments = _create_signed_contract_payments(client)
    paid_payment_id = payments[0]["id"]
    overdue_payment_id = payments[1]["id"]

    pay_response = client.patch(
        f"/api/payments/{paid_payment_id}/pay",
        json={"payment_method": "alipay"},
        headers=tenant_headers,
    )
    assert pay_response.status_code == 200
    paid_payment = pay_response.get_json()["data"]
    assert paid_payment["status"] == "paid"
    assert paid_payment["transaction_no"].startswith("PAY")

    refund_response = client.patch(
        f"/api/payments/{paid_payment_id}/refund",
        json={"reason": "test refund"},
        headers=landlord_headers,
    )
    assert refund_response.status_code == 200
    assert refund_response.get_json()["data"]["status"] == "refunded"

    with app.app_context():
        payment = db.session.get(Payment, overdue_payment_id)
        payment.due_date = utc_now().date() - timedelta(days=1)
        db.session.commit()

    overdue_response = client.post("/api/payments/overdue-scan", headers=landlord_headers)
    assert overdue_response.status_code == 200
    assert overdue_response.get_json()["data"]["updated_count"] == 1

    fail_response = client.patch(
        f"/api/payments/{overdue_payment_id}/fail",
        json={"payment_method": "bank", "reason": "test failure"},
        headers=tenant_headers,
    )
    assert fail_response.status_code == 200
    assert fail_response.get_json()["data"]["status"] == "failed"
