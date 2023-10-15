import os
from datetime import datetime
from unittest import mock

import httpx
import pytest
import typer
from hypothesis import given
from hypothesis import strategies as st
from pytest_httpx import httpx_mock
from pytest_httpx import HTTPXMock

from nstimes.departure import Departure
from nstimes.main import printers
from nstimes.printers import ConsolePrinter
from nstimes.printers import ConsoleTablePrinter
from nstimes.printers import PixelClockPrinter
from tests.strategies import departure_strategy


@given(departures=st.lists(departure_strategy(), min_size=1, max_size=20))
def test_departure_can_be_printed_as_ascii(departures):
    printer = ConsolePrinter()
    for departure in departures:
        printer.add_departure(departure)
    printer.generate_output()


@given(departures=st.lists(departure_strategy(), min_size=1, max_size=20))
def test_departure_can_be_printed_as_table(departures):
    printer = ConsoleTablePrinter()
    for departure in departures:
        printer.add_departure(departure)
    printer.generate_output()


def test_set_title():
    os.environ["PIXEL_CLOCK_IP"] = "something"
    for p in printers.values():
        printer = p()
        printer.set_title("Test")
        assert printer.title == "Test"


@pytest.fixture
def mock_env(monkeypatch):
    with mock.patch.dict(os.environ, clear=True):
        yield


def test_departure_cant_be_printed_on_undefined_pixelclock():
    os.environ.clear()
    with pytest.raises(typer.Exit, match=r"1"):
        PixelClockPrinter()


def test_departure_cant_be_printed_on_unreachable_pixelclock(httpx_mock: HTTPXMock):
    httpx_mock.add_exception(httpx.ReadTimeout("Unable to read within timeout"))
    os.environ.clear()
    os.environ["PIXEL_CLOCK_IP"] = "something"
    printer = PixelClockPrinter()
    departure = Departure("SPR", "14b", datetime.now())
    printer.add_departure(departure)
    with pytest.raises(typer.Exit, match=r"2"):
        printer.generate_output()


def test_bad_request_returns_1_pixelclock(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=400)
    os.environ.clear()
    os.environ["PIXEL_CLOCK_IP"] = "something"
    printer = PixelClockPrinter()
    departure = Departure("SPR", "14b", datetime.now())
    printer.add_departure(departure)
    with pytest.raises(typer.Exit, match=r"1"):
        printer.generate_output()


def test_status_200_raises_no_error_pixelclock(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200)
    os.environ.clear()
    os.environ["PIXEL_CLOCK_IP"] = "something"
    printer = PixelClockPrinter()
    departure = Departure("SPR", "14b", datetime.now())
    printer.add_departure(departure)
    printer.generate_output()


def test_pixelclock_empty_departures_cant_print_output(httpx_mock: HTTPXMock):
    os.environ.clear()
    os.environ["PIXEL_CLOCK_IP"] = "something"
    printer = PixelClockPrinter()
    with pytest.raises(typer.Exit, match=r"1"):
        printer.generate_output()
