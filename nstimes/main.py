from datetime import datetime, timedelta
import os
from dataclasses import dataclass
import typer
from typing_extensions import Annotated
import httpx
import json
from importlib.metadata import version
from rich import print
from dotenv import load_dotenv

from nstimes.types.departure import Departure

# Load environment variables from the .env file
load_dotenv()

DATETIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%S%z"
MINUTES_NEEDED = 0
SCRIPT_DIR = os.path.dirname(__file__)
STATIONS_FILE = os.path.join(SCRIPT_DIR,"stations.json")
API_URL="https://gateway.apiportal.ns.nl/reisinformatie-api/api"


app = typer.Typer(
    help="Find your next train home while you are in CLI. I used the Dutch Railway Services (Nederlandse Spoorwegen) API to make myself this tool.",
    pretty_exceptions_show_locals=os.getenv("SHOW_LOCALS"),
)

@app.command(hidden=True)
def update_stations_json(token: Annotated[str, typer.Option(help="Token to talk with the NS API",
                                                            envvar="NS_API_TOKEN")]):

    headers = {
        'Cache-Control': 'no-cache',
        'Ocp-Apim-Subscription-Key': token
    }
    query_params = {
        "countryCodes": "nl"
    }

    try:
        with httpx.Client() as client:
            response = client.get(url="{API_URL}/v2/stations",headers=headers, params=query_params)
            response.raise_for_status()
    except httpx.ReadTimeout:
            print("Request timed out (which can happen)")
            typer.Exit(0)
    except httpx.HTTPStatusError:
            typer.Exit(1)

    # get list of stations to uic code
    data = response.json()['payload']
    uic_mapping = {d["namen"]["lang"]: d["UICCode"] for d in data}
    with open(STATIONS_FILE, 'w', encoding="utf-8") as file:
        json.dump(uic_mapping, file)
    return uic_mapping

def complete_name(incomplete: str):
    for name in get_uic_mapping():
        if name.startswith(incomplete):
            yield name


def get_uic_mapping() -> dict[str,str]:
    with open(STATIONS_FILE, "r",encoding="utf-8") as file:
        uic_mapping = json.load(file)
    return uic_mapping

@app.command(help="Provide train type, platform and departure times of an A -> B journey")
def journey(start: Annotated[str, typer.Option(help="Start station", autocompletion=complete_name)],
         end: Annotated[str, typer.Option(help="Stop station", autocompletion=complete_name)],
         token: Annotated[str, typer.Option(help="Token to talk with the NS API", envvar="NS_API_TOKEN")]):

    uic_mapping = get_uic_mapping()
    print(f"Journeys from {start} -> {end} at {datetime.now().strftime('%H:%M')}")


    query_params = {
        'originUicCode': uic_mapping[start],
        'destinationUicCode': uic_mapping[end],
    }
    headers= {
        'Cache-Control': 'no-cache',
        'Ocp-Apim-Subscription-Key': token
    }

    try:
        with httpx.Client() as client:
            response = client.get(url=f"{API_URL}/v3/trips", params=query_params, headers=headers)
            response.raise_for_status()
    except httpx.ReadTimeout:
            print("Request timed out (which can happen)")
            typer.Exit(0)
    except httpx.HTTPStatusError:
            typer.Exit(1)

    trips = response.json()["trips"]
    for trip in trips:
        trip = trip["legs"][0]
        origin = trip["origin"]

        track = int(origin.get('actualTrack', origin.get('plannedTrack', -1)))

        planned_departure_time = datetime.strptime(origin['plannedDateTime'],DATETIME_FORMAT_STRING)

        actual_departure_time = origin.get('actualDateTime')
        if actual_departure_time is not None:
            actual_departure_time = datetime.strptime(actual_departure_time, DATETIME_FORMAT_STRING)

        train_type = trip['product']['categoryCode']

        departure = Departure(train_type=train_type,
                              platform=track,
                              planned_departure_time=planned_departure_time,
                              actual_departure_time=actual_departure_time)
        if departure.time_left_minutes >= 0:
            print(f"{departure}")

def version_callback(value: bool):
    if value:
        print(f"nstimes version: {version(__package__)}")
        raise typer.Exit()

@app.callback()
def main(
    version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True),
):
    return
