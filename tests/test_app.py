"""
Tests for the Mergington High School Activities API.
Uses the Arrange-Act-Assert (AAA) pattern.
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
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 9

    def test_activity_has_required_fields(self):
        # Act
        response = client.get("/activities")

        # Assert
        for activity in response.json().values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity

    def test_participants_is_a_list(self):
        # Act
        response = client.get("/activities")

        # Assert
        for activity in response.json().values():
            assert isinstance(activity["participants"], list)


class TestSignup:
    def test_signup_success(self):
        # Arrange
        email = "newstudent@mergington.edu"

        # Act
        response = client.post("/activities/Chess Club/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_signup_adds_participant(self):
        # Arrange
        email = "newstudent@mergington.edu"

        # Act
        client.post("/activities/Chess Club/signup", params={"email": email})

        # Assert
        participants = client.get("/activities").json()["Chess Club"]["participants"]
        assert email in participants

    def test_signup_unknown_activity_returns_404(self):
        # Arrange
        email = "test@mergington.edu"

        # Act
        response = client.post("/activities/Unknown Activity/signup", params={"email": email})

        # Assert
        assert response.status_code == 404

    def test_signup_duplicate_returns_400(self):
        # Arrange
        email = "michael@mergington.edu"  # already registered in Chess Club

        # Act
        response = client.post("/activities/Chess Club/signup", params={"email": email})

        # Assert
        assert response.status_code == 400

    def test_signup_full_activity_returns_400(self):
        # Arrange
        activity_name = "Chess Club"
        max_p = activities[activity_name]["max_participants"]
        for i in range(max_p):
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"student{i}@mergington.edu"},
            )

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "overflow@mergington.edu"},
        )

        # Assert
        assert response.status_code == 400


class TestUnregister:
    def test_unregister_success(self):
        # Arrange
        email = "michael@mergington.edu"

        # Act
        response = client.delete("/activities/Chess Club/signup", params={"email": email})

        # Assert
        assert response.status_code == 200

    def test_unregister_removes_participant(self):
        # Arrange
        email = "michael@mergington.edu"

        # Act
        client.delete("/activities/Chess Club/signup", params={"email": email})

        # Assert
        participants = client.get("/activities").json()["Chess Club"]["participants"]
        assert email not in participants

    def test_unregister_unknown_activity_returns_404(self):
        # Arrange
        email = "michael@mergington.edu"

        # Act
        response = client.delete("/activities/Unknown Activity/signup", params={"email": email})

        # Assert
        assert response.status_code == 404

    def test_unregister_not_signed_up_returns_404(self):
        # Arrange
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete("/activities/Chess Club/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
