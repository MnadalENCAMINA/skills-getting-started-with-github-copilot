"""
Tests for the Mergington High School Activities API.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset participants to original state before each test."""
    original = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, participants in original.items():
        activities[name]["participants"] = participants


class TestGetActivities:
    def test_returns_all_activities(self):
        response = client.get("/activities")
        assert response.status_code == 200
        assert len(response.json()) == 9

    def test_activity_has_required_fields(self):
        data = client.get("/activities").json()
        for activity in data.values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity

    def test_participants_is_a_list(self):
        data = client.get("/activities").json()
        for activity in data.values():
            assert isinstance(activity["participants"], list)


class TestSignup:
    def test_signup_success(self):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert response.status_code == 200
        assert "newstudent@mergington.edu" in response.json()["message"]

    def test_signup_adds_participant(self):
        email = "newstudent@mergington.edu"
        client.post("/activities/Chess Club/signup", params={"email": email})
        assert email in client.get("/activities").json()["Chess Club"]["participants"]

    def test_signup_unknown_activity_returns_404(self):
        response = client.post(
            "/activities/Unknown Activity/signup",
            params={"email": "test@mergington.edu"},
        )
        assert response.status_code == 404

    def test_signup_duplicate_returns_400(self):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},  # already registered
        )
        assert response.status_code == 400

    def test_signup_full_activity_returns_400(self):
        activity_name = "Chess Club"
        max_p = activities[activity_name]["max_participants"]
        for i in range(max_p):
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"student{i}@mergington.edu"},
            )
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "overflow@mergington.edu"},
        )
        assert response.status_code == 400


class TestUnregister:
    def test_unregister_success(self):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 200

    def test_unregister_removes_participant(self):
        email = "michael@mergington.edu"
        client.delete("/activities/Chess Club/signup", params={"email": email})
        assert email not in client.get("/activities").json()["Chess Club"]["participants"]

    def test_unregister_unknown_activity_returns_404(self):
        response = client.delete(
            "/activities/Unknown Activity/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 404

    def test_unregister_not_signed_up_returns_404(self):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "notregistered@mergington.edu"},
        )
        assert response.status_code == 404
