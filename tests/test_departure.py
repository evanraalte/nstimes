from datetime import datetime
from datetime import timedelta

from hypothesis import given

from nstimes.departure import Departure
from tests.strategies import delay_strategy
from tests.strategies import time_strategy


# Define a Hypothesis strategy for generating random delays in minutes
@given(time=time_strategy, delay=delay_strategy)
def test_departure_delay(time: datetime, delay: int) -> None:
    # Calculate the expected time by adding the delay to the original time
    expected_time = time + timedelta(minutes=delay)

    departure = Departure(
        _actual_departure_time=expected_time,
        planned_departure_time=time,
        planned_destination_time=time + timedelta(minutes=30),
        _actual_destination_time=expected_time + timedelta(minutes=30),
        train_type="IC",
        platform="14b",
    )
    assert departure.delay_minutes_departure == delay
    assert delay >= 0


@given(time_now=time_strategy, delay=delay_strategy)
def test_departure_minutes_left(delay: int, time_now: datetime) -> None:
    time_departure = time_now + timedelta(minutes=delay)
    departure = Departure(
        planned_departure_time=time_departure,
        train_type="IC",
        platform="14b",
        planned_destination_time=time_departure + timedelta(minutes=30),
    )
    assert departure.calc_time_left_minutes(reference_time=time_now) == delay
    assert departure.delay_minutes_departure == 0
