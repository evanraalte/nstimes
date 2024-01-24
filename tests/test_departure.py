from datetime import datetime
from datetime import timedelta

from hypothesis import given

from nstimes.departure import Departure
from nstimes.departure import Time
from tests.strategies import delay_strategy
from tests.strategies import time_strategy


# Define a Hypothesis strategy for generating random delays in minutes
@given(time=time_strategy, delay=delay_strategy)
def test_departure_delay(time: datetime, delay: int) -> None:
    TRIP_TIME = timedelta(minutes=30)

    departure_time = Time(planned=time, actual=time + timedelta(minutes=delay))
    arrival_time = Time(
        planned=time + TRIP_TIME, actual=time + timedelta(minutes=delay) + TRIP_TIME
    )

    departure = Departure(
        departure_time=departure_time,
        arrival_time=arrival_time,
        train_type="IC",
        platform="14b",
    )
    assert departure.departure_time.delay_minutes == delay
    assert delay >= 0


@given(time_now=time_strategy, delay=delay_strategy)
def test_departure_minutes_left(delay: int, time_now: datetime) -> None:
    TRIP_TIME = timedelta(minutes=30)

    departure_time = Time(planned=time_now, actual=time_now + timedelta(minutes=delay))
    arrival_time = Time(
        planned=time_now + TRIP_TIME,
        actual=time_now + TRIP_TIME + timedelta(minutes=delay),
    )

    departure = Departure(
        departure_time=departure_time,
        train_type="IC",
        platform="14b",
        arrival_time=arrival_time,
    )
    assert departure.calc_time_left_minutes(reference_time=time_now) == delay
    assert departure.departure_time.delay_minutes == delay
