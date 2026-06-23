"""
Integration tests for FastAPI application endpoints using AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client, reset_activities):
        """Test that root endpoint redirects to /static/index.html"""
        # Arrange: Set up the test client (already done via fixture)
        
        # Act: Make GET request to root
        response = client.get("/", follow_redirects=False)
        
        # Assert: Verify redirect response
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint."""

    def test_get_all_activities_returns_dict(self, client, reset_activities):
        """Test that GET /activities returns all activities with correct structure"""
        # Arrange: Prepare expected activity count
        expected_count = 9
        
        # Act: Make GET request to /activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Verify response status and data structure
        assert response.status_code == 200
        assert len(data) == expected_count
        assert "Chess Club" in data
        assert data["Chess Club"]["description"] is not None
        assert "participants" in data["Chess Club"]
        assert isinstance(data["Chess Club"]["participants"], list)

    def test_get_activities_contains_all_required_fields(self, client, reset_activities):
        """Test that each activity has all required fields"""
        # Arrange: Define required fields
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act: Make GET request and retrieve activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Verify all activities have required fields
        for activity_name, activity in data.items():
            assert all(field in activity for field in required_fields), \
                f"Activity '{activity_name}' missing required fields"

    def test_get_activities_participants_are_strings(self, client, reset_activities):
        """Test that participants list contains email strings"""
        # Arrange: No special setup needed
        
        # Act: Get activities and check a specific one
        response = client.get("/activities")
        data = response.json()
        chess_participants = data["Chess Club"]["participants"]
        
        # Assert: Verify participants are strings (emails)
        assert len(chess_participants) > 0
        assert all(isinstance(p, str) and "@" in p for p in chess_participants)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, client, reset_activities):
        """Test successful signup of new participant"""
        # Arrange: Prepare signup data
        activity_name = "Chess Club"
        new_email = "testuser@mergington.edu"
        
        # Act: Sign up new participant
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert: Verify signup successful and state changed
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant added to activity
        check_response = client.get("/activities")
        participants = check_response.json()[activity_name]["participants"]
        assert new_email in participants

    def test_signup_activity_not_found_returns_404(self, client, reset_activities):
        """Test signup to non-existent activity returns 404"""
        # Arrange: Use non-existent activity name
        non_existent_activity = "Non-Existent Club"
        email = "student@mergington.edu"
        
        # Act: Attempt to sign up for non-existent activity
        response = client.post(
            f"/activities/{non_existent_activity}/signup",
            params={"email": email}
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_participant_returns_400(self, client, reset_activities):
        """Test signup of already-signed-up participant returns 400"""
        # Arrange: Use existing participant
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in participants
        
        # Act: Attempt duplicate signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert: Verify 400 response and error message
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_participants_across_activities(self, client, reset_activities):
        """Test signing up same participant to multiple activities"""
        # Arrange: Prepare participant and activities
        new_email = "multiuser@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act: Sign up to first activity
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": new_email}
        )
        
        # Act: Sign up to second activity
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": new_email}
        )
        
        # Assert: Both signups successful
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify participant in both activities
        check_response = client.get("/activities")
        data = check_response.json()
        assert new_email in data[activity1]["participants"]
        assert new_email in data[activity2]["participants"]

    def test_signup_to_at_capacity_activity(self, client, reset_activities):
        """Test signup to at-capacity activity (if capacity is enforced)"""
        # Arrange: Create activity at capacity by using one with few spots
        # Note: Current app doesn't enforce capacity, so this documents current behavior
        activity_name = "Debate Team"  # max_participants: 14
        new_email = "testuser@mergington.edu"
        
        # Act: Sign up new participant
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert: Current implementation allows signup (no capacity check)
        # This test documents that capacity is NOT enforced in current app
        # If capacity enforcement is added, this test can be modified
        assert response.status_code == 200


class TestRemoveParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_success(self, client, reset_activities):
        """Test successful removal of participant from activity"""
        # Arrange: Prepare participant to remove
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act: Remove participant
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email_to_remove}
        )
        
        # Assert: Verify removal successful
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant removed from activity
        check_response = client.get("/activities")
        participants = check_response.json()[activity_name]["participants"]
        assert email_to_remove not in participants

    def test_remove_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test removal from non-existent activity returns 404"""
        # Arrange: Use non-existent activity
        non_existent_activity = "Non-Existent Club"
        email = "student@mergington.edu"
        
        # Act: Attempt to remove from non-existent activity
        response = client.delete(
            f"/activities/{non_existent_activity}/participants",
            params={"email": email}
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_remove_nonexistent_participant_returns_404(self, client, reset_activities):
        """Test removal of non-existent participant returns 404"""
        # Arrange: Use non-existent participant email
        activity_name = "Chess Club"
        non_existent_email = "notinlist@mergington.edu"
        
        # Act: Attempt to remove non-existent participant
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": non_existent_email}
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_remove_and_resign_participant(self, client, reset_activities):
        """Test removing and re-signing up same participant"""
        # Arrange: Prepare participant and activity
        activity_name = "Chess Club"
        email = "testuser@mergington.edu"
        
        # Act: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Signup successful
        assert signup_response.status_code == 200
        
        # Act: Remove participant
        remove_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Removal successful
        assert remove_response.status_code == 200
        
        # Act: Re-sign up same participant
        resignup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Re-signup successful (participant can sign up again after removal)
        assert resignup_response.status_code == 200
        
        # Verify participant is in activity
        check_response = client.get("/activities")
        participants = check_response.json()[activity_name]["participants"]
        assert email in participants
