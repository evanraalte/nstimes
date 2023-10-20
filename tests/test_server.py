import pytest
from fastapi import Response
from fastapi import status
from fastapi.testclient import TestClient

from nstimes import server


def mocked_response(
    start: str, end: str, rdc3339_datetime: str, token: str
) -> Response:
    return Response(status_code=200)


def test_production_has_no_docs(client_production: TestClient) -> None:
    response = client_production.get("/docs")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_journey_returns_200(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(server, "get_departures", mocked_response)
    response = client.get(
        "/journey", params={"start": "Amersfoort Centraal", "end": "Utrecht Centraal"}
    )
    assert response.status_code == 200


def test_no_token_raises_500(client_no_token: TestClient) -> None:
    response = client_no_token.get(
        "/journey", params={"start": "Amersfoort Centraal", "end": "Utrecht Centraal"}
    )
    assert response.status_code == 500
    assert "Could not find NS_API_TOKEN" in response.text


def test_journey_bad_start_returns_400(client: TestClient) -> None:
    response = client.get(
        "/journey", params={"start": "Bad input", "end": "Utrecht Centraal"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_journey_bad_end_returns_400(client: TestClient) -> None:
    response = client.get(
        "/journey", params={"start": "Amersfoort Centraal", "end": "Bad input"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_stations(client_no_token: TestClient) -> None:
    response = client_no_token.get("/stations")
    assert response.status_code == 200
    data = response.json()
    assert "Amersfoort Centraal" in data
