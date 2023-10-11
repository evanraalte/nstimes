from typer.testing import CliRunner
from importlib.metadata import version
from nstimes.main import app
import nstimes

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
    lines = result.stdout.splitlines()
    for line in lines:
        if line.startswith("Journeys from"):
            continue
        spr = "SPR" in line
        ic = "IC" in line
        assert ic ^ spr
