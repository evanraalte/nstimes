import os
from typing import Generator
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi import Response
from fastapi.testclient import TestClient
from pytest_httpx import HTTPXMock

from nstimes import server
from nstimes.server import get_token


@pytest.fixture(name="client", scope="function")
def create_client() -> Generator[TestClient, None, None]:
    from nstimes.server import app

    def get_mock_token() -> str:
        return "something"

    app.dependency_overrides[get_token] = get_mock_token
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="client_no_token", scope="function")
def create_client_no_token() -> Generator[TestClient, None, None]:
    from nstimes.server import app

    client = TestClient(app)
    yield client


def mocked_response(
    start: str, end: str, rdc3339_datetime: str, token: str
) -> Response:
    return Response(status_code=200)


def test_nsau_returns_200(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server, "get_departures", mocked_response)
    response = client.get("/nsau")
    assert response.status_code == 200


def test_no_token_raises_500(client_no_token: TestClient) -> None:
    response = client_no_token.get("/nsau")
    assert response.status_code == 500
