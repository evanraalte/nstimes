import json
import tempfile
from importlib.metadata import version
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import settings
from hypothesis import Verbosity
from typer.testing import CliRunner

from nstimes.main import app
from nstimes.main import complete_name
from nstimes.main import STATIONS_FILE
from tests.strategies import two_different_stations_strategy

runner = CliRunner()


def test_app_version_is_correct():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert version("nstimes") in result.stdout


def test_app_gets_train_times():
    result = runner.invoke(
        app, ["journey", "--start", "Amersfoort Centraal", "--end", "Utrecht Centraal"]
    )
    assert result.exit_code == 0


def test_app_gets_train_times_table():
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
def test_app_gets_random_train_times(pair):
    station1, station2 = pair
    assert station1 != station2
    result = runner.invoke(app, ["journey", "--start", station1, "--end", station2])
    assert result.exit_code == 0
    lines = result.stdout.splitlines()
    for line in lines:
        if line.startswith("Journeys from"):
            continue
        assert any(tt in line for tt in ["S", "ST", "SPR", "IC"])


def test_complete_name():
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


def test_update_stations():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_json_file = Path(temp_dir) / "test.json"

        # Invoke the 'update-stations-json' command with the temporary file path
        result = runner.invoke(
            app, ["update-stations-json", "--path", str(temp_json_file)]
        )

        # Assert that the command ran successfully (exit code is 0)
        assert result.exit_code == 0

        # Assert that the temporary JSON file was created
        assert temp_json_file.exists()

        # Assert that the temporary JSON file is a valid JSON file
        with temp_json_file.open("r") as json_file:
            data = json.load(json_file)
            assert isinstance(data, dict)
            for key, value in data.items():
                assert isinstance(key, str)
                assert isinstance(value, str)
    # The temporary directory and its contents will be automatically cleaned up
