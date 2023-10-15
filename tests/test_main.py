import json
import tempfile
from importlib.metadata import version
from pathlib import Path

import httpx
import pytest
from hypothesis import given
from hypothesis import settings
from hypothesis import Verbosity
from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from nstimes.main import app
from nstimes.main import complete_name
from tests.strategies import two_different_stations_strategy

runner = CliRunner()


def test_app_version_is_correct() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert version("nstimes") in result.stdout


def test_app_gets_train_times() -> None:
    result = runner.invoke(
        app, ["journey", "--start", "Amersfoort Centraal", "--end", "Utrecht Centraal"]
    )
    assert result.exit_code == 0


def test_app_gets_train_times_table() -> None:
    result = runner.invoke(
        app,
        [
            "journey",
            "--start",
            "Amersfoort Centraal",
            "--end",
            "Utrecht Centraal",
            "--printer",
            "table",
        ],
    )
    assert result.exit_code == 0


@pytest.mark.skip("Too long")
@given(pair=two_different_stations_strategy())
@settings(max_examples=10, deadline=None, verbosity=Verbosity.verbose)
def test_app_gets_random_train_times(pair: tuple[str, str]) -> None:
    station1, station2 = pair
    assert station1 != station2
    result = runner.invoke(app, ["journey", "--start", station1, "--end", station2])
    assert result.exit_code == 0
    lines = result.stdout.splitlines()
    for line in lines:
        if line.startswith("Journeys from"):
            continue
        assert any(tt in line for tt in ["S", "ST", "SPR", "IC"])


def test_complete_name() -> None:
    lut = {
        "apple": "fruit",
        "banana": "fruit",
        "carrot": "vegetable",
        "cherry": "fruit",
    }

    # Test cases
    assert list(complete_name(lut, "c")) == ["carrot", "cherry"]
    assert list(complete_name(lut, "b")) == ["banana"]
    assert list(complete_name(lut, "a")) == ["apple"]
    assert list(complete_name(lut, "z")) == []


def test_update_stations_writes_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_json_file = Path(temp_dir) / "test.json"

        result = runner.invoke(
            app, ["update-stations-json", "--path", str(temp_json_file)]
        )

        assert result.exit_code == 0

        assert temp_json_file.exists()

        with temp_json_file.open("r") as json_file:
            data = json.load(json_file)
            assert isinstance(data, dict)
            for key, value in data.items():
                assert isinstance(key, str)
                assert isinstance(value, str)


def test_update_stations_bad_response_does_not_write_file(
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(method="GET", status_code=400)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_json_file = Path(temp_dir) / "test.json"

        result = runner.invoke(
            app, ["update-stations-json", "--path", str(temp_json_file)]
        )

        assert result.exit_code == 1
        assert not temp_json_file.exists()


def test_update_stations_time_out_does_not_write_file_exits_2(
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_exception(httpx.ReadTimeout("Unable to read within timeout"))
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_json_file = Path(temp_dir) / "test.json"

        result = runner.invoke(
            app, ["update-stations-json", "--path", str(temp_json_file)]
        )

        assert result.exit_code == 2
        assert not temp_json_file.exists()


def test_exception_raising(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(httpx.ReadTimeout("Unable to read within timeout"))

    with httpx.Client() as client:
        with pytest.raises(httpx.ReadTimeout):
            client.get("https://test_url")
