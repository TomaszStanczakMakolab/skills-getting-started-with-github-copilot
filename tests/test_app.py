import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create test client
client = TestClient(app)

# Original activities data for reset
ORIGINAL_ACTIVITIES = {
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
    "Soccer Club": {
        "description": "Practice soccer skills and play friendly matches",
        "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["linda@mergington.edu", "ryan@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Team-based basketball training and interschool games",
        "schedule": "Mondays and Thursdays, 5:00 PM - 6:30 PM",
        "max_participants": 15,
        "participants": ["noah@mergington.edu", "ava@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore painting, drawing, and mixed-media art projects",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["mia@mergington.edu", "jack@mergington.edu"]
    },
    "Drama Club": {
        "description": "Rehearse and perform short plays, improv, and acting exercises",
        "schedule": "Thursdays, 4:30 PM - 6:00 PM",
        "max_participants": 20,
        "participants": ["sophia@mergington.edu", "liam@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Prepare for science competitions with experiments and problem solving",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["noah@mergington.edu", "emma@mergington.edu"]
    },
    "Debate Team": {
        "description": "Practice public speaking and competitive debate techniques",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["olivia@mergington.edu", "daniel@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    activities.clear()
    activities.update(ORIGINAL_ACTIVITIES.copy())

class TestActivitiesEndpoint:
    """Test cases for GET /activities endpoint"""

    def test_get_activities_success(self):
        # Arrange: No special setup needed, activities are reset

        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: Check status code and response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # All activities present
        assert "Chess Club" in data
        assert "Programming Class" in data

        # Check structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

class TestSignupEndpoint:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        # Arrange: Choose an activity and new email
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"

        # Act: Make POST request to signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert: Check success response
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Signed up {new_email} for {activity_name}" == data["message"]

        # Verify participant was added
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert new_email in activities_data[activity_name]["participants"]

    def test_signup_activity_not_found(self):
        # Arrange: Use non-existent activity
        invalid_activity = "NonExistent Club"
        email = "test@mergington.edu"

        # Act: Attempt to signup for invalid activity
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )

        # Assert: Check error response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" == data["detail"]

    def test_signup_already_registered(self):
        # Arrange: Use an email already in Chess Club
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # From original data

        # Act: Attempt to signup again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert: Check error response
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student already signed up for this activity" == data["detail"]

class TestUnregisterEndpoint:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        # Arrange: Choose an activity and existing participant
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act: Make DELETE request to unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_email}
        )

        # Assert: Check success response
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Unregistered {existing_email} from {activity_name}" == data["message"]

        # Verify participant was removed
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert existing_email not in activities_data[activity_name]["participants"]

    def test_unregister_activity_not_found(self):
        # Arrange: Use non-existent activity
        invalid_activity = "NonExistent Club"
        email = "test@mergington.edu"

        # Act: Attempt to unregister from invalid activity
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )

        # Assert: Check error response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" == data["detail"]

    def test_unregister_not_registered(self):
        # Arrange: Use an email not in the activity
        activity_name = "Chess Club"
        not_registered_email = "notregistered@mergington.edu"

        # Act: Attempt to unregister non-participant
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": not_registered_email}
        )

        # Assert: Check error response
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student is not registered for this activity" == data["detail"]

class TestRootEndpoint:
    """Test cases for GET / endpoint"""

    def test_root_redirect(self):
        # Arrange: No special setup

        # Act: Make GET request to root
        response = client.get("/")

        # Assert: Check redirect response
        assert response.status_code == 200  # FastAPI handles redirect internally in test client
        # The redirect goes to /static/index.html, but in test client it might return the HTML
        # Since it's a redirect, we can check if it contains expected content
        assert "Mergington High School" in response.text