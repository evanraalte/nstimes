from dataclasses import dataclass
from datetime import datetime

from rich.table import Table


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
        time_left = self.actual_departure_time - datetime.now(
            tz=self.actual_departure_time.tzinfo
        )
        return int(time_left.total_seconds() / 60)
