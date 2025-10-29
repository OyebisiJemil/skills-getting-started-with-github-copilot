from fastapi.testclient import TestClient
from urllib.parse import quote
import pytest

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Expect at least one known activity from the in-memory DB
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity_name = "Chess Club"
    email = "test.user@example.com"

    # Ensure email is not already present (clean state)
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    # Sign up
    res = client.post(f"/activities/{quote(activity_name)}/signup", params={"email": email})
    assert res.status_code == 200
    body = res.json()
    assert "Signed up" in body.get("message", "")

    # Verify participant shows up in GET
    res2 = client.get("/activities")
    assert res2.status_code == 200
    data = res2.json()
    assert email in data[activity_name]["participants"]

    # Duplicate signup should be rejected
    res3 = client.post(f"/activities/{quote(activity_name)}/signup", params={"email": email})
    assert res3.status_code == 400

    # Unregister
    res4 = client.delete(f"/activities/{quote(activity_name)}/signup", params={"email": email})
    assert res4.status_code == 200
    assert "Unregistered" in res4.json().get("message", "")

    # Verify removed
    res5 = client.get("/activities")
    assert res5.status_code == 200
    data2 = res5.json()
    assert email not in data2[activity_name]["participants"]


def test_nonexistent_activity_errors():
    fake = "NoSuchActivity"
    res = client.post(f"/activities/{quote(fake)}/signup", params={"email": "a@b.com"})
    assert res.status_code == 404
    res2 = client.delete(f"/activities/{quote(fake)}/signup", params={"email": "a@b.com"})
    assert res2.status_code == 404
*** End Patch