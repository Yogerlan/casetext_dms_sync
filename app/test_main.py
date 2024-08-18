import os

from fastapi import status
from fastapi.testclient import TestClient

from .main import app, today

os.environ["TESTING"] = ""
client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "pong"}


def test_sync():
    # Test wrong params.
    since = "/".join(today.split("-"))
    response = client.get("/sync", params={
        "since": since
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test nonsense date.
    since = f"{today[:4]}-20-{today[8:]}"
    response = client.get("/sync", params={
        "since": since
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test future date.
    since = f"{str(int(today[:4]) - 1)}{today[4:]}"
    until = f"{str(int(today[:4]) + 1)}{today[4:]}"
    response = client.get("/sync", params={
        "since": since,
        "until": until
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test switched dates.
    since = f"{str(int(today[:4]) - 1)}{today[4:]}"
    response = client.get("/sync", params={
        "since": today,
        "until": since
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test valid responses
    response = client.get("/sync", params={
        "since": "2024-08-16",
        "until": "2024-08-17"
    })
    assert response.status_code == 200
    operations = response.json()
    assert len(operations) == 4
