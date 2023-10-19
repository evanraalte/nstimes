from dataclasses import dataclass
from dataclasses import field
from dataclasses import InitVar
from datetime import datetime
from typing import Optional

from rich.table import Table


@dataclass
class Departure:
    train_type: str
    platform: str
    planned_departure_time: datetime
    actual_departure_time: datetime = field(init=False)
    actual_departure_time_init: InitVar[Optional[datetime]] = None

    def __post_init__(self, actual_departure_time_init: Optional[datetime]) -> None:
        self.actual_departure_time = (
            actual_departure_time_init or self.planned_departure_time
        )

    @property
    def delay_minutes(self) -> int:
        delay = self.actual_departure_time - self.planned_departure_time
        return int(delay.total_seconds() / 60)

    def time_left_minutes(self, reference_time: datetime = datetime.now()) -> int:
        reference_time = reference_time.replace(
            tzinfo=self.actual_departure_time.tzinfo
        )
        time_left = self.actual_departure_time - reference_time
        return int(time_left.total_seconds() / 60)
