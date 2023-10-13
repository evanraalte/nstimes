from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta

from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st

from nstimes.departure import Departure

# Define a Hypothesis strategy for generating times in the format "HH:MM"
time_strategy = st.datetimes(
    min_value=datetime(2023, 1, 1),  # Specify an appropriate minimum date and time
    max_value=datetime(2023, 12, 31),  # Specify an appropriate maximum date and time
)
# Define a Hypothesis strategy for generating random delays in minutes
delay_strategy = st.integers(min_value=0, max_value=120)  # Adjust the range as needed


@st.composite
def departure_strategy(draw):
    planned = draw(
        st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2100, 12, 31))
    )
    time_difference_seconds = draw(st.integers(min_value=1, max_value=3600))
    actual = planned + timedelta(seconds=time_difference_seconds)
    return Departure(
        train_type="SPR",
        platform="14b",
        planned_departure_time=planned,
        actual_departure_time=actual,
    )
