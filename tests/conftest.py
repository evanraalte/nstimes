from typing import Generator
from fastapi.testclient import TestClient
import pytest

from nstimes.server import Settings, get_settings


@pytest.fixture(name="client", scope="function")
def create_client() -> Generator[TestClient, None, None]:
    from nstimes.server import app

    def get_mock_settings() -> Settings:
        return Settings(ns_api_token="something")

    app.dependency_overrides[get_settings] = get_mock_settings
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="client_production", scope="function")
def create_client_production() -> Generator[TestClient, None, None]:
    from nstimes.server import get_app

    settings = Settings(ns_api_token="something", virtual_host="myhost")
    app = get_app(limiter=None, settings=settings)
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="client_no_token", scope="function")
def create_client_no_token() -> Generator[TestClient, None, None]:
    from nstimes.server import app

    client = TestClient(app)
    yield client
