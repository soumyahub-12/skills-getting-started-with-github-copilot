"""
Tests for the Mergington High School API

Tests cover:
- Getting all activities
- Signing up for activities
- Error cases (invalid activity, duplicate signup)
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Soccer practice and friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["grace@mergington.edu"]
        },
        "Music Band": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 12,
            "participants": ["tyler@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore physics, chemistry, and biology through experiments",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        }
    }
    
    # Clear and restore
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


# Test getting all activities
def test_get_activities(client, reset_activities):
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Basketball Team" in data


def test_get_activities_content(client, reset_activities):
    """Test that activities have required fields"""
    response = client.get("/activities")
    data = response.json()
    
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


# Test signing up for activities
def test_signup_new_participant(client, reset_activities):
    """Test signing up a new participant for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]


def test_signup_updates_participants(client, reset_activities):
    """Test that signup actually adds participant to the activity"""
    # Get initial count
    response = client.get("/activities")
    initial_count = len(response.json()["Chess Club"]["participants"])
    
    # Sign up new participant
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    # Check updated count
    response = client.get("/activities")
    new_count = len(response.json()["Chess Club"]["participants"])
    
    assert new_count == initial_count + 1
    assert "newstudent@mergington.edu" in response.json()["Chess Club"]["participants"]


# Test error cases
def test_signup_nonexistent_activity(client, reset_activities):
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_signup_duplicate_participant(client, reset_activities):
    """Test that a student can't sign up for the same activity twice"""
    # Try to sign up someone already registered
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_multiple_signups_different_activities(client, reset_activities):
    """Test that a student can sign up for multiple activities"""
    student_email = "versatile@mergington.edu"
    
    # Sign up for first activity
    response1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": student_email}
    )
    assert response1.status_code == 200
    
    # Sign up for second activity
    response2 = client.post(
        "/activities/Basketball Team/signup",
        params={"email": student_email}
    )
    assert response2.status_code == 200
    
    # Verify both signups
    response = client.get("/activities")
    activities_data = response.json()
    
    assert student_email in activities_data["Chess Club"]["participants"]
    assert student_email in activities_data["Basketball Team"]["participants"]


def test_all_activities_exist(client, reset_activities):
    """Test that all expected activities are present"""
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Soccer Club",
        "Art Studio",
        "Music Band",
        "Debate Team",
        "Science Club"
    ]
    
    response = client.get("/activities")
    data = response.json()
    
    for activity in expected_activities:
        assert activity in data, f"Activity '{activity}' not found in response"


def test_activity_max_participants(client, reset_activities):
    """Test that activities have max_participants field"""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity_data in data.items():
        assert "max_participants" in activity_data
        assert isinstance(activity_data["max_participants"], int)
        assert activity_data["max_participants"] > 0
