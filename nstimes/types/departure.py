from dataclasses import dataclass
from datetime import datetime
from rich.table import Table

def red(text):
    return f"[bold red]{text}[/bold red]"
def cyan(text):
    return f"[bold cyan]{text}[/bold cyan]"
def green(text):
    return f"[bold green]{text}[/bold green]"

@dataclass
class Departure:
    train_type: str
    platform: str
    planned_departure_time: datetime
    actual_departure_time: datetime = None

    def __post_init__(self):
        if self.actual_departure_time is None:
            self.actual_departure_time = self.planned_departure_time

    @property
    def delay_minutes(self) -> int:
        delay = self.actual_departure_time - self.planned_departure_time
        return int(delay.total_seconds() / 60)

    @property
    def time_left_minutes(self) -> int:
        time_left = self.actual_departure_time - datetime.now(tz=self.actual_departure_time.tzinfo)
        return int(time_left.total_seconds() / 60)

    def add_row_to_table(self, table: Table):
        act_dep_time_str = self.planned_departure_time.strftime('%H:%M')
        delay_str = "" if self.delay_minutes == 0 else red(f"+{self.delay_minutes}")
        table.add_row(self.train_type, cyan(self.platform), f"{cyan(self.time_left_minutes)} min", f"{green(act_dep_time_str)}{delay_str}")

    def __str__(self):
        act_dep_time_str = self.planned_departure_time.strftime('%H:%M')
        delay_str = "" if self.delay_minutes == 0 else red(self.delay_minutes)
        return f"{self.train_type:<3s} p.{self.platform:>3s} in {self.time_left_minutes:02d} min ({act_dep_time_str}{delay_str})"
