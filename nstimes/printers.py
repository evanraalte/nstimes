from typing import Protocol

from rich import print
from rich.console import Console
from rich.table import Column
from rich.table import Table

from nstimes.departure import Departure


class Printer(Protocol):
    def generate_output(self):
        """generates output in the console"""

    def set_title(self, title: str):
        """Sets the title of the generated output"""

    def add_departure(self, departure: Departure):
        """adds a row to the departures"""


def red(text):
    return f"[bold red]{text}[/bold red]"


def cyan(text):
    return f"[bold cyan]{text}[/bold cyan]"


def green(text):
    return f"[bold green]{text}[/bold green]"


class ConsolePrinter:
    def __init__(self):
        self.buf = ""
        self.title = ""

    def generate_output(self):
        print(self.title)
        print("\n")
        print(self.buf)

    def set_title(self, title: str):
        self.title = title

    def add_departure(self, departure: Departure):
        act_dep_time_str = departure.planned_departure_time.strftime("%H:%M")
        delay_str = (
            "" if departure.delay_minutes == 0 else red(f"+{departure.delay_minutes}")
        )

        self.buf += f"{departure.train_type:<3s} p.{departure.platform:>3s} in {departure.time_left_minutes():>2d} min ({act_dep_time_str}{delay_str})\n"


class ConsoleTablePrinter:
    def __init__(self):
        self.table = Table(
            Column("Train", justify="left"),
            Column("Platform", justify="right"),
            Column("Leaves in", justify="right"),
            Column("Departure time", justify="right"),
        )

    def generate_output(self):
        Console().print(self.table)

    @property
    def title(self):
        return self.table.title

    def set_title(self, title: str):
        self.table.title = title

    def add_departure(self, departure: Departure):
        act_dep_time_str = departure.planned_departure_time.strftime("%H:%M")
        delay_str = (
            "" if departure.delay_minutes == 0 else red(f"+{departure.delay_minutes}")
        )

        self.table.add_row(
            departure.train_type,
            cyan(departure.platform),
            f"{cyan(departure.time_left_minutes)} min",
            f"{green(act_dep_time_str)}{delay_str}",
        )
