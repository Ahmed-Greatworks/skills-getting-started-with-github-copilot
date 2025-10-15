import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"].endswith("/static/index.html")

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert isinstance(activities, dict)

def test_signup_for_activity():
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # Try signing up
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    # Verify student is in activity
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]
    
    # Try signing up again (should fail)
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_from_activity():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Using an existing participant
    
    # Try unregistering
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    
    # Verify student is removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
    
    # Try unregistering again (should fail)
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": email})
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]

def test_activity_not_found():
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"
    
    # Try signing up for nonexistent activity
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
    
    # Try unregistering from nonexistent activity
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": email})
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]