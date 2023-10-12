import json
import pytest
from typer.testing import CliRunner
from importlib.metadata import version
from nstimes.main import STATIONS_FILE, app
from hypothesis import Verbosity, given, settings, strategies as st

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



@st.composite
def two_different_stations_strategy(draw):
    with open(STATIONS_FILE, "r",encoding="utf-8") as file:
        uic_mapping = json.load(file)
    station_names = list(uic_mapping.keys())
    name1 = draw(st.sampled_from(station_names))
    remaining_names = [name for name in station_names if name != name1]
    name2 = draw(st.sampled_from(remaining_names))
    return (name1, name2)



@pytest.mark.skip("Too long")
@given(pair=two_different_stations_strategy())
@settings(max_examples=10, deadline=None, verbosity=Verbosity.verbose)
def test_app_gets_random_train_times(pair):
    station1, station2 = pair
    assert station1 != station2
    result = runner.invoke(
        app, ["journey", "--start", station1, "--end", station2]
    )
    assert result.exit_code == 0
    lines = result.stdout.splitlines()
    for line in lines:
        if line.startswith("Journeys from"):
            continue
        assert any(tt in line for tt in ["S", "ST", "SPR", "IC"])
