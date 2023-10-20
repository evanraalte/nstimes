import os
from datetime import datetime
from typing import Any
from unittest import mock

import httpx
import pytest
import typer
from hypothesis import given
from hypothesis import strategies as st
from pytest_httpx import httpx_mock
from pytest_httpx import HTTPXMock

from nstimes.departure import Departure
from nstimes.printers import ConsolePrinter
from nstimes.printers import ConsoleTablePrinter
from nstimes.printers import get_printer
from nstimes.printers import PixelClockPrinter
from nstimes.printers import Printer
from tests.strategies import departure_strategy


@given(departures=st.lists(departure_strategy(), min_size=1, max_size=20))
def test_departure_can_be_printed_as_ascii(departures: list[Departure]) -> None:
    printer = ConsolePrinter()
    for departure in departures:
        printer.add_departure(departure)
    printer.generate_output()


@given(departures=st.lists(departure_strategy(), min_size=1, max_size=20))
def test_departure_can_be_printed_as_table(departures: list[Departure]) -> None:
    printer = ConsoleTablePrinter()
    for departure in departures:
        printer.add_departure(departure)
    printer.generate_output()


def test_set_title() -> None:
    os.environ["PIXEL_CLOCK_IP"] = "something"

    printer: ConsolePrinter = ConsolePrinter()
    printer.title = "Test"
    assert printer.title == "Test"

    printer2: ConsoleTablePrinter = ConsoleTablePrinter()
    printer2.title = "Test2"
    assert printer2.title == "Test2"

    printer3: PixelClockPrinter = PixelClockPrinter()
    printer3.title = "Test3"
    assert printer3.title == "Test3"


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch) -> Any:
    with mock.patch.dict(os.environ, clear=True):
        yield


def test_departure_cant_be_printed_on_undefined_pixelclock() -> None:
    os.environ.clear()
    with pytest.raises(typer.Exit, match=r"1"):
        PixelClockPrinter()


def test_departure_cant_be_printed_on_unreachable_pixelclock(
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_exception(httpx.ReadTimeout("Unable to read within timeout"))
    os.environ.clear()
    os.environ["PIXEL_CLOCK_IP"] = "something"
    printer = PixelClockPrinter()
    departure = Departure(
        train_type="SPR", platform="14b", planned_departure_time=datetime.now()
    )
    printer.add_departure(departure)
    with pytest.raises(typer.Exit, match=r"2"):
        printer.generate_output()


def test_bad_request_returns_1_pixelclock(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=400)
    os.environ.clear()
    os.environ["PIXEL_CLOCK_IP"] = "something"
    printer = PixelClockPrinter()
    departure = Departure(
        train_type="SPR", platform="14b", planned_departure_time=datetime.now()
    )
    printer.add_departure(departure)
    with pytest.raises(typer.Exit, match=r"1"):
        printer.generate_output()


def test_status_200_raises_no_error_pixelclock(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=200)
    os.environ.clear()
    os.environ["PIXEL_CLOCK_IP"] = "something"
    printer = PixelClockPrinter()
    departure = Departure(
        train_type="SPR", platform="14b", planned_departure_time=datetime.now()
    )
    printer.add_departure(departure)
    printer.generate_output()


def test_pixelclock_empty_departures_cant_print_output(httpx_mock: HTTPXMock) -> None:
    os.environ.clear()
    os.environ["PIXEL_CLOCK_IP"] = "something"
    printer = PixelClockPrinter()
    with pytest.raises(typer.Exit, match=r"1"):
        printer.generate_output()


def test_invalid_printer_raises_exit_1() -> None:
    with pytest.raises(typer.Exit, match=r"1"):
        get_printer("invalid")  # type: ignore
