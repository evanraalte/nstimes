import functools
import json
import os
from datetime import datetime
from enum import Enum
from importlib.metadata import version

import httpx
import typer
from dotenv import load_dotenv
from typing_extensions import Annotated

from nstimes.departure import Departure
from nstimes.printers import ConsolePrinter
from nstimes.printers import ConsoleTablePrinter
from nstimes.printers import PixelClockPrinter
from nstimes.printers import Printer

# Load environment variables from the .env file
load_dotenv()

DATETIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%S%z"
MINUTES_NEEDED = 0
SCRIPT_DIR = os.path.dirname(__file__)
STATIONS_FILE = os.path.join(SCRIPT_DIR, "stations.json")
DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%H:%M"


class PrinterChoice(str, Enum):
    table = "table"
    ascii = "ascii"
    pixelclock = "pixelclock"


printers = {
    "table": ConsoleTablePrinter,
    "ascii": ConsolePrinter,
    "pixelclock": PixelClockPrinter,
}


def convert_to_rfc3339(time: str, date: str) -> str:
    datetime_obj = datetime.strptime(f"{date} {time}", f"{DATE_FORMAT} {TIME_FORMAT}")
    rfc3339_str = datetime_obj.isoformat()
    return rfc3339_str


def get_headers(token):
    return {"Cache-Control": "no-cache", "Ocp-Apim-Subscription-Key": token}


app = typer.Typer(
    help="Find your next train home while you are in CLI. I used the Dutch Railway Services (Nederlandse Spoorwegen) API to make myself this tool.",
    pretty_exceptions_show_locals=os.getenv("SHOW_LOCALS"),
)


def httpx_get(token, query_params, api: str):
    API_URL = "https://gateway.apiportal.ns.nl/reisinformatie-api/api"
    try:
        with httpx.Client() as client:
            response = client.get(
                url=f"{API_URL}/{api}", headers=get_headers(token), params=query_params
            )
            response.raise_for_status()
            return response
    except httpx.ReadTimeout:
        raise typer.Exit(2)
    except httpx.HTTPStatusError:
        raise typer.Exit(1)


@app.command(help="Generate stations lookup, should not be neccesary", hidden=True)
def update_stations_json(
    token: Annotated[
        str, typer.Option(help="Token to talk with the NS API", envvar="NS_API_TOKEN")
    ],
    path: Annotated[
        str, typer.Option(help="Token to talk with the NS API", envvar="NS_API_TOKEN")
    ] = STATIONS_FILE,
):
    query_params = {"countryCodes": "nl"}
    response = httpx_get(token=token, query_params=query_params, api="v2/stations")
    # get list of stations to uic code
    data = response.json()["payload"]
    uic_mapping = {d["namen"]["lang"]: d["UICCode"] for d in data}
    with open(path, "w", encoding="utf-8") as file:
        json.dump(uic_mapping, file)
    typer.Exit(0)


def get_uic_mapping() -> dict[str, str]:
    with open(STATIONS_FILE, "r", encoding="utf-8") as file:
        uic_mapping = json.load(file)
    return uic_mapping


def complete_name(lut: dict[str, str], incomplete: str):
    for name in lut:
        if name.startswith(incomplete):
            yield name


complete_station_name = lambda incomplete: complete_name(
    lut=get_uic_mapping(), incomplete=incomplete
)


@app.command(
    help="Provide train type, platform and departure times of an A -> B journey"
)
def journey(
    start: Annotated[
        str, typer.Option(help="Start station", autocompletion=complete_station_name)
    ],
    end: Annotated[
        str, typer.Option(help="Stop station", autocompletion=complete_station_name)
    ],
    token: Annotated[
        str, typer.Option(help="Token to talk with the NS API", envvar="NS_API_TOKEN")
    ],
    time: Annotated[
        str, typer.Option(help=f"Time to departure ({TIME_FORMAT})")
    ] = datetime.now().strftime("%H:%M"),
    date: Annotated[
        str, typer.Option(help=f"Date to departure ({DATE_FORMAT})")
    ] = datetime.now().strftime("%d-%m-%Y"),
    printer: PrinterChoice = PrinterChoice.ascii.value,
):
    printer: Printer = printers[printer]()

    uic_mapping = get_uic_mapping()

    query_params = {
        "originUicCode": uic_mapping[start],
        "destinationUicCode": uic_mapping[end],
        "dateTime": convert_to_rfc3339(time, date),
    }
    response = httpx_get(token=token, query_params=query_params, api="v3/trips")

    trips = response.json()["trips"]

    printer.set_title(f"Journeys from {start} -> {end} at {date} {time}")

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
            actual_departure_time=actual_departure_time,
        )
        if departure.time_left_minutes() >= 0:
            printer.add_departure(departure)

    printer.generate_output()
    typer.Exit(0)


def version_callback(value: bool):
    if value:
        print(f"nstimes version: {version(__package__)}")
        raise typer.Exit(0)


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Print version info",
    ),
):
    return


if __name__ == "__main__":
    app()  # pragma: no cover
