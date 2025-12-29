"""
Pytest configuration and fixtures for ITKARS Assessment Platform tests.
"""
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.database import get_database
from app.config import settings


# Use a separate test database (same server, different DB name)
TEST_DB_NAME = f"{settings.DB_NAME}_test"


@pytest.fixture(scope="session")
async def test_db():
    """Create a test database connection using the configured MongoDB."""
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[TEST_DB_NAME]
    
    # Clear all collections before tests
    try:
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].drop()
    except Exception as e:
        print(f"Note: Could not clear test collections: {e}")
    
    yield db
    
    # Cleanup after all tests
    try:
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].drop()
    except Exception as e:
        print(f"Note: Could not cleanup test collections: {e}")
    
    client.close()


@pytest.fixture()
async def client(test_db) -> AsyncGenerator:
    """Create an async test client with database override."""
    # Override the database dependency
    def get_test_db():
        return test_db
    
    app.dependency_overrides[get_database] = get_test_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sync_client() -> Generator:
    """Create a sync test client for simple tests."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def admin_token(client, test_db) -> str:
    """Create an admin user and return JWT token."""
    # Clean up any existing admin
    await test_db.admins.delete_many({"email": "testadmin@example.com"})
    
    # Register admin
    response = await client.post(
        "/api/auth/admin/register",
        json={
            "name": "Test Admin",
            "email": "testadmin@example.com",
            "password": "testpassword123"
        }
    )
    
    # Login to get token
    response = await client.post(
        "/api/auth/admin/login",
        json={
            "email": "testadmin@example.com",
            "password": "testpassword123"
        }
    )
    
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token) -> dict:
    """Return authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
async def sample_base_question(client, admin_token, test_db) -> dict:
    """Create a sample base question."""
    response = await client.post(
        "/api/questions/base",
        json={
            "topic": "Python",
            "difficulty": "Medium",
            "description": "Test question about Python basics"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return response.json()


@pytest.fixture
async def sample_variant(client, admin_token, sample_base_question, test_db) -> dict:
    """Create a sample question variant."""
    response = await client.post(
        "/api/questions/variants",
        json={
            "question_id": sample_base_question["id"],
            "question_text": "What is the output of print(2 + 2)?",
            "options": ["2", "4", "22", "Error"],
            "correct_index": 1
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Approve the variant
    variant = response.json()
    await client.put(
        f"/api/questions/variants/{variant['id']}/approve",
        json={"approved": True},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    return variant


@pytest.fixture
async def sample_test_link(client, admin_token, sample_variant, test_db) -> dict:
    """Create a sample test link."""
    response = await client.post(
        "/api/test/generate-link",
        json={
            "candidate_name": "Test Candidate",
            "candidate_email": "candidate@example.com",
            "num_questions": 5,
            "time_per_question": 10
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return response.json()


@pytest.fixture
def mock_gemini():
    """Mock Gemini API responses."""
    with patch("app.services.gemini_service.genai") as mock:
        mock_model = MagicMock()
        mock_model.generate_content.return_value.text = """
        [
            {
                "question_text": "What value does print(2 + 2) display?",
                "options": ["2", "4", "22", "Error"],
                "correct_index": 1
            },
            {
                "question_text": "What is the result of adding 2 and 2 in Python?",
                "options": ["2", "4", "22", "Error"],
                "correct_index": 1
            }
        ]
        """
        mock.GenerativeModel.return_value = mock_model
        yield mock
