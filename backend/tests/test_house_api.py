from tests.conftest import login_user, register_user


def _house_payload(**overrides):
    payload = {
        "title": "市中心两居室",
        "city": "上海",
        "district": "浦东新区",
        "address_detail": "世纪大道 100 号",
        "layout": "2室1厅",
        "area": 86.5,
        "rent": 7200,
        "deposit": 7200,
        "status": "available",
    }
    payload.update(overrides)
    return payload


def test_landlord_can_publish_and_public_can_browse_house(client):
    register_user(client, "landlord_001", role="landlord", real_name="Landlord One")
    headers = login_user(client, "landlord_001")

    created = client.post("/api/houses", json=_house_payload(), headers=headers)
    assert created.status_code == 201
    house = created.get_json()["data"]
    assert house["status"] == "available"
    assert house["landlord"]["username"] == "landlord_001"

    house_id = house["id"]
    listing = client.get("/api/houses?city=上海")
    assert listing.status_code == 200
    assert listing.get_json()["data"]["pagination"]["total"] == 1

    detail = client.get(f"/api/houses/{house_id}")
    assert detail.status_code == 200
    assert detail.get_json()["data"]["title"] == "市中心两居室"


def test_tenant_cannot_create_house(client):
    register_user(client, "tenant_002", role="tenant")
    headers = login_user(client, "tenant_002")

    response = client.post("/api/houses", json=_house_payload(), headers=headers)

    assert response.status_code == 403
    assert response.get_json()["code"] == 4003
