"""
Pytest configuration and fixtures for FastAPI application tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient instance for API testing."""
    return TestClient(app)


@pytest.fixture
def activities_data():
    """
    Provide fresh in-memory activities database for each test.
    Matches the initial state in src/app.py.
    """
    return {
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
        "Soccer Team": {
            "description": "Join the school soccer team for practices and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["anna@mergington.edu", "ben@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swim laps, improve technique, and prepare for meets",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["nora@mergington.edu", "luke@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["mia@mergington.edu", "jack@mergington.edu"]
        },
        "Drama Club": {
            "description": "Practice acting, stagecraft, and prepare for school performances",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["sara@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore science topics beyond the classroom",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["liam@mergington.edu", "ella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking skills and compete in debate tournaments",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["zoe@mergington.edu", "ryan@mergington.edu"]
        }
    }


@pytest.fixture
def reset_activities(monkeypatch, activities_data):
    """
    Reset app.activities to fresh data before each test.
    Ensures no state leakage between tests.
    """
    import src.app as app_module
    monkeypatch.setattr(app_module, "activities", activities_data)
    return activities_data
