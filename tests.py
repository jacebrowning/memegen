from apistar.test import TestClient
from app import app


def test_list_templates():
    client = TestClient(app)
    response = client.get('http://localhost/templates/')
    assert response.status_code == 200
    assert response.json() == []
