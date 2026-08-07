import pytest

from app import create_app
from config import TestConfig


@pytest.fixture
def client():
    """
    Create a Flask test client.
    """
    app = create_app(TestConfig)


    with app.test_client() as client:
        yield client



def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["status"] == "healthy"