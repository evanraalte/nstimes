import json
import os
from datetime import datetime
from importlib.metadata import version
from typing import Generator

import httpx
import typer
from dotenv import load_dotenv
from typing_extensions import Annotated

from nstimes.departure import get_departures
from nstimes.printers import get_printer
from nstimes.printers import PrinterChoice
from nstimes.utils import convert_to_rfc3339
from nstimes.utils import DATE_FORMAT
from nstimes.utils import get_uic_mapping
from nstimes.utils import httpx_get
from nstimes.utils import STATIONS_FILE
from nstimes.utils import TIME_FORMAT

# Load environment variables from the .env file
load_dotenv()


app = typer.Typer(
    help="Find your next train home while you are in CLI. I used the Dutch Railway Services (Nederlandse Spoorwegen) API to make myself this tool.",
    pretty_exceptions_show_locals=os.getenv("SHOW_LOCALS"),
)


@app.command(help="Generate stations lookup, should not be neccesary", hidden=True)
def update_stations_json(
    token: Annotated[
        str, typer.Option(help="Token to talk with the NS API", envvar="NS_API_TOKEN")
    ],
    path: Annotated[str, typer.Option(help="Path for stations.json")] = STATIONS_FILE,
) -> None:
    query_params = {"countryCodes": "nl"}
    response = httpx_get(token=token, query_params=query_params, api="v2/stations")
    # get list of stations to uic code
    data = response.json()["payload"]
    uic_mapping = {d["namen"]["lang"]: d["UICCode"] for d in data}
    with open(path, "w", encoding="utf-8") as file:
        json.dump(uic_mapping, file)
    typer.Exit(0)


def complete_name(lut: dict[str, str], incomplete: str) -> Generator[str, None, None]:
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
    printer_choice: Annotated[
        PrinterChoice, typer.Option(help="The type of printer")
    ] = PrinterChoice.ascii,
) -> None:
    printer = get_printer(printer_choice)

    printer.title = f"Journeys from {start} -> {end} at {date} {time}"
    rdc3339_datetime = convert_to_rfc3339(time, date)
    departures = get_departures(
        start=start, end=end, token=token, rdc3339_datetime=rdc3339_datetime
    )
    for departure in departures:
        if departure.time_left_minutes() >= 0:
            printer.add_departure(departure)
    printer.generate_output()


def version_callback(value: bool) -> None:
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
) -> None:
    return


if __name__ == "__main__":
    app()  # pragma: no cover
