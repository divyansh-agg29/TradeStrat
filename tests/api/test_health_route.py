def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["status"] == "healthy"