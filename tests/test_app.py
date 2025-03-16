"""
Unit tests for flooding web app (async version)
"""

import pytest
import json
import uuid
import time
import sys

from flood_app import create_app, settings


@pytest.fixture
def client():
    """Set up a test client for the Flask app"""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture()
def headers():
    """Create valid header info with API_KEY"""
    return {"Authorization": f"Bearer {settings.API_KEY}"}


@pytest.fixture(scope="module")
def valid_uuid():
    """Create an uuid for valid request and check its status"""
    return str(uuid.uuid4())


@pytest.fixture(scope="module")
def timeout_uuid():
    """Create an uuid for time out request and check its status"""
    return str(uuid.uuid4())


def test_app_creation(client):
    """Ensure the Flask app initializes correctly"""
    assert client is not None


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Flood app is running" in response.data


def test_submit_simulation_unauthorized(client):
    """Test submitting a simulation no Authorization header is provided."""
    response = client.post("/submit_simulation", json={})
    assert response.status_code == 401
    assert response.json["error"] == "Unauthorized"


def test_submit_simulation_forbidden(client):
    """Test submitting a simulation with an invalid API key."""
    headers = {"Authorization": "Bearer INVALID_KEY"}
    response = client.post("/submit_simulation", headers=headers, json={})
    assert response.status_code == 403
    assert response.json["error"] == "Invalid API Key"


def test_submit_simulation_time_out(client, timeout_uuid, headers, shared_datadir):
    """Test submitting a simulation with time out error."""
    with open(shared_datadir / "test_request_json_valid.json") as fp:
        request_data = json.load(fp)
    request_data["simulationId"] = timeout_uuid
    request_data["timeout"] = 5  # adjust time out with shorter value for testing

    response = client.post(
        "/submit_simulation",
        headers=headers,
        data=json.dumps(request_data),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert (
        f"Request {request_data['simulationId']} is received."
        in response.json["message"]
    )


def test_submit_simulation_valid_request(client, valid_uuid, headers, shared_datadir):
    """Test submitting a valid request"""
    with open(shared_datadir / "test_request_json_valid.json") as fp:
        request_data = json.load(fp)
    request_data["simulationId"] = valid_uuid

    response = client.post(
        "/submit_simulation",
        headers=headers,
        data=json.dumps(request_data),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert (
        f"Request {request_data['simulationId']} is received."
        in response.json["message"]
    )


def test_submit_simulation_invalid_id(client, headers):
    """Test submitting a simulation with an invalid UUID"""
    request_data = {
        "simulationId": "invalid-uuid",
        "map": "some map data",
        "timeout": 100000,
    }
    response = client.post(
        "/submit_simulation",
        headers=headers,
        data=json.dumps(request_data),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "Please provide a valid simulation ID." in response.json["error"]


def test_submit_simulation_existing_id(client, valid_uuid, headers):
    """Test submitting a simulation with an existing UUID"""
    request_data = {
        "simulationId": valid_uuid,
        "map": "some map data",
        "timeout": 100000,
    }
    response = client.post(
        "/submit_simulation",
        headers=headers,
        data=json.dumps(request_data),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "Simulation ID already exists." in response.json["error"]


def test_submit_simulation_missing_map(client, headers):
    """Test submitting a request with missing map data"""
    simulation_id = str(uuid.uuid4())  # Generate a valid UUID
    request_data = {
        "simulationId": simulation_id,
        "map": "",
        "timeout": 100000,
    }
    response = client.post(
        "/submit_simulation",
        headers=headers,
        data=json.dumps(request_data),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "Missing valid map data." in response.json["error"]


def test_submit_simulation_invalid_map_data(client, headers):
    """Test submitting a request with invalid map data"""
    simulation_id = str(uuid.uuid4())  # Generate a UUID
    request_data = {
        "simulationId": simulation_id,
        "map": "invalid_map_data",
        "timeout": 100000,
    }
    response = client.post(
        "/submit_simulation",
        headers=headers,
        data=json.dumps(request_data),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "Invalid map json string" in response.json["error"]


def test_check_status_not_found_id(client):
    """Test checking the status of a non-existing simulation id"""
    simulation_id = str(uuid.uuid4())
    response = client.get(f"/check_status/{simulation_id}")

    assert response.status_code == 400
    assert "Simulation ID not found." in response.json["error"]


def test_check_status_invalid_id(client):
    """Test checking the status of an invalid uuid"""
    simulation_id = "invalid_id"
    response = client.get(f"/check_status/{simulation_id}")

    assert response.status_code == 400
    assert "Please provide a valid simulation ID." in response.json["error"]


@pytest.mark.skipif(sys.platform == "win32", reason="Skipping test on Windows")
def test_check_status_timeout_id(client, timeout_uuid):
    """Test checking the status of a timeout simulation id"""
    time.sleep(50)
    response = client.get(f"/check_status/{timeout_uuid}")

    assert response.status_code == 500
    assert (
        f"Request {timeout_uuid} is failed. Error info: Simulation timeout exceeded"
        in response.json["error"]
    )


def test_check_status_valid_id(client, valid_uuid):
    """Test checking the status of a valid simulation id"""
    response = client.get(f"/check_status/{valid_uuid}")

    assert response.status_code == 200
    assert (
        "processing" in response.json["message"]
        or "complete" in response.json["message"]
    )
