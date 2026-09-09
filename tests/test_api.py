import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("app"))

from main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_documents_endpoint():
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_facts_endpoint():
    response = client.get("/api/facts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_relationships_endpoint():
    response = client.get("/api/relationships")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
