import json
from datetime import datetime
from datetime import timedelta

from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st

from nstimes.departure import Departure
from nstimes.utils import STATIONS_FILE

# Define a Hypothesis strategy for generating times in the format "HH:MM"
time_strategy: st.SearchStrategy[datetime] = st.datetimes(
    min_value=datetime(2023, 1, 1),  # Specify an appropriate minimum date and time
    max_value=datetime(2023, 12, 31),  # Specify an appropriate maximum date and time
)
# Define a Hypothesis strategy for generating random delays in minutes
delay_strategy: st.SearchStrategy[datetime] = st.integers(
    min_value=0, max_value=120
)  # Adjust the range as needed


@st.composite
def departure_strategy(draw: st.DrawFn) -> st.SearchStrategy[Departure]:
    planned = draw(time_strategy)
    time_difference_seconds = draw(st.integers(min_value=1, max_value=3600))
    actual = planned + timedelta(seconds=time_difference_seconds)
    return Departure(
        train_type="SPR",
        platform="14b",
        planned_departure_time=planned,
        _actual_departure_time=actual,
    )


@st.composite
def two_different_stations_strategy(
    draw: st.DrawFn,
) -> st.SearchStrategy[tuple[str, str]]:
    with open(STATIONS_FILE, "r", encoding="utf-8") as file:
        uic_mapping = json.load(file)
    station_names = list(uic_mapping.keys())
    name1 = draw(st.sampled_from(station_names))
    remaining_names = [name for name in station_names if name != name1]
    name2 = draw(st.sampled_from(remaining_names))
    return (name1, name2)
