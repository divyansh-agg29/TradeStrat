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
