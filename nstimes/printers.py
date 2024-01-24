from enum import Enum
from typing import Protocol

import httpx
import typer
from rich import print
from rich.console import Console
from rich.table import Column
from rich.table import Table
from rich.text import Text

from nstimes.departure import Departure
from nstimes.styles import cancelled
from nstimes.styles import cyan
from nstimes.styles import green
from nstimes.styles import red


class Printer(Protocol):
    title: str = ""

    def generate_output(self) -> None:
        """generates output in the console"""

    def add_departure(self, departure: Departure) -> None:
        """adds a row to the departures"""


class ConsolePrinter:
    def __init__(self) -> None:
        self.buf = ""
        self.title = ""
        self.lines: list[str] = []

    def generate_output(self) -> None:
        print(self.title)
        print("\n")
        for line in self.lines:
            print(line)

    def add_departure(self, departure: Departure) -> None:
        line = f"{departure.train_type:<3s} p.{departure.platform:>3s} in {departure.calc_time_left_minutes():>2d} min {departure.departure_time} -> {departure.arrival_time}"
        if departure.cancelled:
            line = cancelled(line)
        self.lines.append(line)


class ConsoleTablePrinter:
    def __init__(self) -> None:
        self.table = Table(
            Column("Train", justify="left"),
            Column("Platform", justify="right"),
            Column("Leaves in", justify="right"),
            Column("Departure time", justify="right"),
            Column("Arrival time", justify="right"),
        )

    def generate_output(self) -> None:
        Console().print(self.table)

    @property
    def title(self) -> str:
        return str(self.table.title)

    @title.setter
    def title(self, value: str) -> None:
        self.table.title = value

    def add_departure(self, departure: Departure) -> None:
        if departure.cancelled:
            self.table.add_row(
                cancelled(departure.train_type),
                cancelled(departure.platform),
                cancelled(f"{departure.time_left_minutes} min"),
                cancelled(str(departure.departure_time)),
                cancelled(str(departure.arrival_time)),
            )
        else:
            self.table.add_row(
                departure.train_type,
                cyan(departure.platform),
                f"{cyan(departure.time_left_minutes)} min",
                f"{departure.departure_time}",
                f"{departure.arrival_time}",
            )


class PrinterChoice(str, Enum):
    table = "table"
    ascii = "ascii"


def get_printer(
    printer_choice: PrinterChoice,
) -> Printer:
    if printer_choice == PrinterChoice.ascii:
        return ConsolePrinter()
    elif printer_choice == PrinterChoice.table:
        return ConsoleTablePrinter()
    else:
        raise typer.Exit(1)
