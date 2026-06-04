from tests.conftest import login_user, register_user


def _create_house(client, headers, **overrides):
    payload = {
        "title": "Metro apartment",
        "city": "Hangzhou",
        "district": "Xihu",
        "community": "West Garden",
        "address_detail": "No. 1 Wenyi Road",
        "layout": "2R1L",
        "area": 88,
        "rent": 5200,
        "deposit": 5200,
        "status": "available",
    }
    payload.update(overrides)
    response = client.post("/api/houses", json=payload, headers=headers)
    assert response.status_code == 201
    return response.get_json()["data"]


def test_search_regions_and_layouts_only_include_available_houses(client):
    register_user(client, "search_landlord", role="landlord")
    headers = login_user(client, "search_landlord")

    _create_house(client, headers, community="West Garden", layout="2R1L", rent=5200)
    _create_house(client, headers, community="West Garden", layout="2R1L", rent=5600)
    _create_house(client, headers, community="East Garden", layout="1R1L", rent=3900)
    _create_house(
        client,
        headers,
        community="Hidden Garden",
        layout="3R2L",
        rent=8200,
        status="draft",
    )

    regions = client.get("/api/search/regions?city=Hangzhou").get_json()["data"]
    assert [item["community"] for item in regions] == ["West Garden", "East Garden"]
    assert regions[0]["house_count"] == 2
    assert regions[0]["min_rent"] == 5200
    assert regions[0]["max_rent"] == 5600

    layouts = client.get("/api/search/layouts?city=Hangzhou").get_json()["data"]
    assert [item["layout"] for item in layouts] == ["2R1L", "1R1L"]
    assert layouts[0]["house_count"] == 2


def test_search_recommendations_use_similarity_then_fallback(client):
    register_user(client, "recommend_landlord", role="landlord")
    headers = login_user(client, "recommend_landlord")

    base = _create_house(client, headers, title="Base", city="Hangzhou", district="Xihu", layout="2R1L")
    similar = _create_house(
        client,
        headers,
        title="Similar layout",
        city="Hangzhou",
        district="Xihu",
        layout="2R1L",
        rent=5400,
    )
    fallback = _create_house(
        client,
        headers,
        title="Fallback",
        city="Shanghai",
        district="Pudong",
        layout="1R1L",
        rent=7200,
    )

    response = client.get(f"/api/search/recommendations?house_id={base['id']}&limit=2")

    assert response.status_code == 200
    items = response.get_json()["data"]
    assert [item["id"] for item in items] == [similar["id"], fallback["id"]]
