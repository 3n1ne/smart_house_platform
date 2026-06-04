from datetime import timedelta

from app.models.base import utc_now
from tests.conftest import login_user, register_user


def test_tenant_rental_history_summarizes_recent_records(client):
    register_user(client, "history_landlord", role="landlord")
    register_user(client, "history_tenant", role="tenant")
    landlord_headers = login_user(client, "history_landlord")
    tenant_headers = login_user(client, "history_tenant")

    house = client.post(
        "/api/houses",
        json={
            "title": "History house",
            "city": "Hangzhou",
            "district": "Xihu",
            "address_detail": "No. 20",
            "layout": "1R1L",
            "area": 50,
            "rent": 3600,
            "deposit": 3600,
            "status": "available",
        },
        headers=landlord_headers,
    ).get_json()["data"]

    client.post(
        "/api/bookings",
        json={
            "house_id": house["id"],
            "appointment_time": (utc_now() + timedelta(days=1)).isoformat(),
        },
        headers=tenant_headers,
    )

    response = client.get("/api/users/rental-history", headers=tenant_headers)

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["summary"]["bookings"] == 1
    assert data["recent_bookings"][0]["house"]["title"] == "History house"
