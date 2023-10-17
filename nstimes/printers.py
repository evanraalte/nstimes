import json
import os
from enum import Enum
from typing import Protocol

import httpx
import typer
from rich import print
from rich.console import Console
from rich.table import Column
from rich.table import Table

from nstimes.departure import Departure


class Printer(Protocol):
    title: str = ""

    def generate_output(self) -> None:
        """generates output in the console"""

    def add_departure(self, departure: Departure) -> None:
        """adds a row to the departures"""


def red(text: str | int) -> str:
    return f"[bold red]{text}[/bold red]"


def cyan(text: str | int) -> str:
    return f"[bold cyan]{text}[/bold cyan]"


def green(text: str | int) -> str:
    return f"[bold green]{text}[/bold green]"


class ConsolePrinter:
    def __init__(self) -> None:
        self.buf = ""
        self.title = ""

    def generate_output(self) -> None:
        print(self.title)
        print("\n")
        print(self.buf)

    def add_departure(self, departure: Departure) -> None:
        act_dep_time_str = departure.planned_departure_time.strftime("%H:%M")
        delay_str = (
            "" if departure.delay_minutes == 0 else red(f"+{departure.delay_minutes}")
        )

        self.buf += f"{departure.train_type:<3s} p.{departure.platform:>3s} in {departure.time_left_minutes():>2d} min ({act_dep_time_str}{delay_str})\n"


class ConsoleTablePrinter:
    def __init__(self) -> None:
        self.table = Table(
            Column("Train", justify="left"),
            Column("Platform", justify="right"),
            Column("Leaves in", justify="right"),
            Column("Departure time", justify="right"),
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
        act_dep_time_str = departure.planned_departure_time.strftime("%H:%M")
        delay_str = (
            "" if departure.delay_minutes == 0 else red(f"+{departure.delay_minutes}")
        )

        self.table.add_row(
            departure.train_type,
            cyan(departure.platform),
            f"{cyan(departure.time_left_minutes())} min",
            f"{green(act_dep_time_str)}{delay_str}",
        )


class PixelClockPrinter:
    def generate_payload(self, departure: Departure) -> str:
        return json.dumps(
            {
                "text": [
                    {
                        "t": f"{departure.actual_departure_time.strftime('%H:%M')}",
                        "c": "FFFFFF" if departure.delay_minutes == 0 else "FF0000",
                    },
                    {"t": f"{departure.platform}", "c": "00FF00"},
                ],
                "stack": False,
                "duration": 10,
                "noScroll": True,
            }
        )

    def __init__(self) -> None:
        try:
            ip = os.environ["PIXEL_CLOCK_IP"]
        except KeyError:
            print("Can't initiate printer, please instantiate env var PIXEL_CLOCK_IP")
            raise typer.Exit(1)
        self.url: str = f"http://{ip}/api/notify"
        self.departures: list[Departure] = []
        self.title: str = ""

    def generate_output(self) -> None:
        try:
            next_departure = next(
                iter(sorted(self.departures, key=lambda d: d.actual_departure_time))
            )
        except StopIteration:
            print("No departures to print")
            raise typer.Exit(1)
        payload = self.generate_payload(next_departure)
        try:
            response = httpx.post(self.url, data=payload)
            response.raise_for_status()
        except (httpx.ReadTimeout, httpx.ConnectError) as exc:
            print(f"Could not reach your clock, got: {exc}")
            raise typer.Exit(2)
        except httpx.HTTPStatusError as exc:
            print(f"Got bad request from your clock, got: {exc}")
            raise typer.Exit(1)
        print("Look at your clock, not here :)")

    def add_departure(self, departure: Departure) -> None:
        self.departures.append(departure)


class PrinterChoice(str, Enum):
    table = "table"
    ascii = "ascii"
    pixelclock = "pixelclock"


def get_printer(
    printer_choice: PrinterChoice,
) -> Printer:
    if printer_choice == PrinterChoice.ascii:
        return ConsolePrinter()
    elif printer_choice == PrinterChoice.table:
        return ConsoleTablePrinter()
    elif printer_choice == PrinterChoice.pixelclock:
        return PixelClockPrinter()
    else:
        raise typer.Exit(1)
