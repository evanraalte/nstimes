from dataclasses import dataclass  # pragma: no cover
from datetime import datetime
from typing import Optional

from pydantic import computed_field

from nstimes.styles import green
from nstimes.styles import red
from nstimes.utils import get_uic_mapping
from nstimes.utils import httpx_get

DATETIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%S%z"


class Time:
    def __init__(self, planned: datetime, actual: Optional[datetime] = None) -> None:
        self.actual = actual or planned
        self.planned = planned

    @property
    def delay_minutes(self) -> int:
        delay = self.actual - self.planned
        return int(delay.total_seconds() / 60)

    def __str__(self) -> str:
        time_str = self.planned.strftime("%H:%M")
        delay_str = "" if self.delay_minutes == 0 else red(f"+{self.delay_minutes}")
        return f"({time_str}{delay_str})"


@dataclass
class Departure:
    train_type: str
    platform: str
    departure_time: Time
    arrival_time: Time
    cancelled: bool = False

    @computed_field  # type: ignore
    @property
    def time_left_minutes(self) -> int:
        return self.calc_time_left_minutes()

    def calc_time_left_minutes(self, reference_time: datetime = datetime.now()) -> int:
        reference_time = reference_time.replace(
            tzinfo=self.departure_time.actual.tzinfo
        )
        time_left = self.departure_time.actual - reference_time
        return int(time_left.total_seconds() / 60)


def parse_time(data: dict) -> Time:  # type: ignore
    planned_time = datetime.strptime(data["plannedDateTime"], DATETIME_FORMAT_STRING)
    actual_time = data.get("actualDateTime")
    if actual_time is not None:
        actual_time = datetime.strptime(actual_time, DATETIME_FORMAT_STRING)
    return Time(planned=planned_time, actual=actual_time)


def get_departures(
    start: str,
    end: str,
    token: str,
    rdc3339_datetime: str,
    max_len: Optional[int] = None,
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
        destination = trip["destination"]
        track = origin.get("actualTrack", origin.get("plannedTrack", "?"))

        cancelled = trip.get("cancelled", False)
        departure_time = parse_time(origin)
        arrival_time = parse_time(destination)

        train_type = trip["product"]["categoryCode"]

        departure = Departure(
            train_type=train_type,
            platform=track,
            departure_time=departure_time,
            arrival_time=arrival_time,
            cancelled=cancelled,
        )
        if departure.time_left_minutes < 0:
            continue
        departures.append(departure)
    return departures
