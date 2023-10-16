from dataclasses import dataclass
from dataclasses import field
from dataclasses import InitVar
from datetime import datetime
from typing import Optional

from nstimes.utils import get_uic_mapping
from nstimes.utils import httpx_get

DATETIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%S%z"


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


def get_departures(
    start: str, end: str, token: str, rdc3339_datetime: str
) -> list[Departure]:
    uic_mapping = get_uic_mapping()

    query_params = {
        "originUicCode": uic_mapping[start],
        "destinationUicCode": uic_mapping[end],
        "dateTime": rdc3339_datetime,
    }
    response = httpx_get(token=token, query_params=query_params, api="v3/trips")
    departures = []
    trips = response.json()["trips"]
    for trip in trips:
        trip = trip["legs"][0]
        origin = trip["origin"]

        track = origin.get("actualTrack", origin.get("plannedTrack", "?"))

        planned_departure_time = datetime.strptime(
            origin["plannedDateTime"], DATETIME_FORMAT_STRING
        )

        actual_departure_time = origin.get("actualDateTime")
        if actual_departure_time is not None:
            actual_departure_time = datetime.strptime(
                actual_departure_time, DATETIME_FORMAT_STRING
            )

        train_type = trip["product"]["categoryCode"]

        departure = Departure(
            train_type=train_type,
            platform=track,
            planned_departure_time=planned_departure_time,
            actual_departure_time_init=actual_departure_time,
        )
        departures.append(departure)
    return departures
