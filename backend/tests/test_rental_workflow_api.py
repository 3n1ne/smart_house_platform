from datetime import UTC, datetime, timedelta

from tests.conftest import login_user, register_user


def test_booking_contract_and_payment_workflow(client):
    register_user(client, "workflow_landlord", role="landlord")
    register_user(client, "workflow_tenant", role="tenant")
    landlord_headers = login_user(client, "workflow_landlord")
    tenant_headers = login_user(client, "workflow_tenant")

    house_response = client.post(
        "/api/houses",
        json={
            "title": "整租一居室",
            "city": "杭州",
            "district": "西湖区",
            "address_detail": "文三路 88 号",
            "layout": "1室1厅",
            "area": 52,
            "rent": 4300,
            "deposit": 4300,
            "status": "available",
        },
        headers=landlord_headers,
    )
    assert house_response.status_code == 201
    house_id = house_response.get_json()["data"]["id"]

    appointment_time = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    booking_response = client.post(
        "/api/bookings",
        json={
            "house_id": house_id,
            "appointment_time": appointment_time,
            "remark": "周末方便看房",
        },
        headers=tenant_headers,
    )
    assert booking_response.status_code == 201
    booking_id = booking_response.get_json()["data"]["id"]

    confirm_response = client.patch(
        f"/api/bookings/{booking_id}/status",
        json={"status": "confirmed"},
        headers=landlord_headers,
    )
    assert confirm_response.status_code == 200
    assert confirm_response.get_json()["data"]["status"] == "confirmed"

    contract_response = client.post(
        "/api/contracts",
        json={
            "booking_id": booking_id,
            "start_date": "2026-06-01",
            "end_date": "2027-06-01",
            "payment_cycle": "monthly",
            "content": "标准租赁合同",
        },
        headers=landlord_headers,
    )
    assert contract_response.status_code == 201
    contract_id = contract_response.get_json()["data"]["id"]

    sign_response = client.patch(
        f"/api/contracts/{contract_id}/sign",
        headers=tenant_headers,
    )
    assert sign_response.status_code == 200
    assert sign_response.get_json()["data"]["status"] == "active"

    payments_response = client.get("/api/payments/mine", headers=tenant_headers)
    assert payments_response.status_code == 200
    payments = payments_response.get_json()["data"]["items"]
    assert len(payments) == 2
    assert {payment["payment_type"] for payment in payments} == {"deposit", "rent"}

    pay_response = client.patch(
        f"/api/payments/{payments[0]['id']}/pay",
        json={"payment_method": "alipay", "transaction_no": "TEST202605090001"},
        headers=tenant_headers,
    )
    assert pay_response.status_code == 200
    assert pay_response.get_json()["data"]["status"] == "paid"
