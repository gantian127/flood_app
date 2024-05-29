"""
unit tests for the app
"""

import pytest
from flood_app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    client = app.test_client()
    yield client


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<form" in response.data


def test_run_model_route_invalid_user_name(client):
    data = {"user_name": ""}
    response = client.post("/run_model", data=data)

    assert response.status_code == 400
    assert b"Please provide a valid user name" in response.data


# test invalid dem file
def test_run_model_route_invalid_dem_file(client):
    data = {
        "user_name": "test_user",
        "dem_file": (open("./test_files/wrong_dem.asc", "rb"), "wrong_dem.asc"),
        "config_file": (
            open("./test_files/config_file.toml", "rb"),
            "config_file.toml",
        ),
    }
    response = client.post("/run_model", data=data, content_type="multipart/form-data")

    assert response.status_code == 400
    assert b"Please upload a valid dem file" in response.data


# test invalid config file
def test_run_model_route_invalid_config_file(client):
    data = {
        "user_name": "test_user",
        "dem_file": (open("./test_files/geer_canyon.txt", "rb"), "geer_canyon.txt"),
        "config_file": (
            open("./test_files/config_file.toml", "rb"),
            "wrong_config.asc",
        ),
    }
    response = client.post("/run_model", data=data, content_type="multipart/form-data")

    assert response.status_code == 400
    assert b"Please provide a valid config file." in response.data


# test valid model run
def test_run_model_route_valid_input(client):
    data = {
        "user_name": "test_user",
        "dem_file": (open("./test_files/geer_canyon.txt", "rb"), "geer_canyon.txt"),
        "config_file": (
            open("./test_files/config_file.toml", "rb"),
            "config_file.toml",
        ),
    }
    response = client.post("/run_model", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert (response.content_type == "application/zip" or
            response.content_type == "application/x-zip-compressed")
