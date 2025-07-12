import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to mi-app"

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_test():
    """Test sample API endpoint"""
    response = client.get("/api/test")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Backend API is working!"
    assert data["project"] == "mi-app"
