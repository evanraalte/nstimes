from hypothesis import given
from hypothesis import strategies as st

from nstimes.main import printers
from nstimes.printers import ConsolePrinter
from nstimes.printers import ConsoleTablePrinter
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
    for p in printers.values():
        printer = p()
        printer.set_title("Test")
        assert printer.title == "Test"
