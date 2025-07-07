import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.services.database import get_db, Base
from app.models.application import Application
from app.models.queue import Queue
from app.models.queue_user import QueueUser, QueueUserStatus
import uuid

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_application():
    db = TestingSessionLocal()
    app = Application(
        name="Test App",
        domain="test.com",
        callback_url="https://test.com/callback",
        api_key="test-api-key-123"
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    db.close()
    return app

@pytest.fixture
def sample_queue(sample_application):
    db = TestingSessionLocal()
    queue = Queue(
        application_id=sample_application.id,
        name="Test Queue",
        max_users_per_minute=10,
        priority=1
    )
    db.add(queue)
    db.commit()
    db.refresh(queue)
    db.close()
    return queue

class TestApplicationsAPI:
    def test_create_application(self):
        response = client.post(
            "/applications/",
            json={
                "name": "Test App",
                "domain": "test.com",
                "callback_url": "https://test.com/callback"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test App"
        assert "api_key" in data

    def test_list_applications(self, sample_application):
        response = client.get("/applications/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test App"

    def test_get_application(self, sample_application):
        response = client.get(f"/applications/{sample_application.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test App"

    def test_update_application(self, sample_application):
        response = client.put(
            f"/applications/{sample_application.id}",
            json={"name": "Updated App"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated App"

    def test_delete_application(self, sample_application):
        response = client.delete(f"/applications/{sample_application.id}")
        assert response.status_code == 204

class TestQueuesAPI:
    def test_create_queue(self, sample_application):
        response = client.post(
            "/queues/",
            json={
                "application_id": str(sample_application.id),
                "name": "Test Queue",
                "max_users_per_minute": 10,
                "priority": 1
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Queue"

    def test_list_queues(self, sample_queue):
        response = client.get("/queues/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Queue"

    def test_update_queue(self, sample_queue):
        response = client.put(
            f"/queues/{sample_queue.id}",
            json={"name": "Updated Queue"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Queue"

    def test_delete_queue(self, sample_queue):
        response = client.delete(f"/queues/{sample_queue.id}")
        assert response.status_code == 204

class TestQueueUsersAPI:
    def test_join_queue(self, sample_queue):
        response = client.post(
            "/join",
            json={
                "queue_id": str(sample_queue.id),
                "visitor_id": "visitor123"
            },
            headers={"app_api_key": "test-api-key-123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["visitor_id"] == "visitor123"
        assert data["status"] == "waiting"
        assert "token" in data

    def test_join_queue_invalid_api_key(self, sample_queue):
        response = client.post(
            "/join",
            json={
                "queue_id": str(sample_queue.id),
                "visitor_id": "visitor123"
            },
            headers={"app_api_key": "invalid-key"}
        )
        assert response.status_code == 401

    def test_join_queue_simulation_mode(self, sample_queue):
        response = client.post(
            "/join?mode=simulation",
            json={
                "queue_id": str(sample_queue.id),
                "visitor_id": "visitor123"
            },
            headers={"app_api_key": "test-api-key-123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    def test_queue_status(self, sample_queue):
        # First join the queue
        join_response = client.post(
            "/join",
            json={
                "queue_id": str(sample_queue.id),
                "visitor_id": "visitor123"
            },
            headers={"app_api_key": "test-api-key-123"}
        )
        token = join_response.json()["token"]
        
        # Check status
        response = client.get(f"/queue_status?token={token}")
        assert response.status_code == 200
        data = response.json()
        assert data["visitor_id"] == "visitor123"

    def test_cancel_queue(self, sample_queue):
        # First join the queue
        join_response = client.post(
            "/join",
            json={
                "queue_id": str(sample_queue.id),
                "visitor_id": "visitor123"
            },
            headers={"app_api_key": "test-api-key-123"}
        )
        token = join_response.json()["token"]
        
        # Cancel
        response = client.post(f"/cancel?token={token}")
        assert response.status_code == 204

class TestDashboardAPI:
    def test_get_summary(self, sample_application, sample_queue):
        response = client.get("/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert "applications" in data
        assert "queues" in data
        assert "total_users" in data

    def test_get_queue_stats(self, sample_queue):
        response = client.get("/dashboard/queue_stats")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["queue_name"] == "Test Queue"

    def test_get_callback_errors(self):
        response = client.get("/dashboard/callback_errors")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_analytics(self, sample_application):
        response = client.get(f"/dashboard/analytics?app_id={sample_application.id}&days=7")
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "daily_joins" in data
        assert "status_distribution" in data 