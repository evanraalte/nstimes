from dataclasses import dataclass
from datetime import datetime


@dataclass
class Departure:
    train_type: str
    platform: int
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

    def __str__(self):
        act_dep_time_str = self.planned_departure_time.strftime('%H:%M')
        delay_str = "" if self.delay_minutes == 0 else f"[bold red]+{self.delay_minutes}[/bold red]"
        return f"{self.train_type} p.{self.platform} in {self.time_left_minutes} min ({act_dep_time_str}{delay_str})"
