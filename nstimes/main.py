from datetime import datetime, timedelta
from os import environ
import typer
from typing_extensions import Annotated
import httpx
import json
from rich.progress import Progress, SpinnerColumn, TextColumn

DATETIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%S%z"
MINUTES_NEEDED = 0
STATIONS_FILE = "nstimes/stations.json"

app = typer.Typer(
    help="Find your next train home while you are in CLI. I used the Dutch Railway Services (Nederlandse Spoorwegen) API to make myself this tool."
)

@app.command(hidden=True)
def update_stations_json(token: Annotated[str, typer.Option(help="Token to talk with the NS API", envvar="NS_API_TOKEN")]):
    with httpx.Client() as client:
        response = client.get(url="https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/stations?countryCodes=nl",headers={
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': token
        })

        # get list of stations to uic code
        data = response.json()['payload']
        UIC_mapping = {d["namen"]["lang"]: d["UICCode"] for d in data}
        with open(STATIONS_FILE, 'w') as file:
            json.dump(UIC_mapping, file)
    return UIC_mapping

def complete_name(incomplete: str):
    completion = []
    with open(STATIONS_FILE, "r") as file:
        UIC_mapping = json.load(file)
    for name in UIC_mapping:
        if name.startswith(incomplete):
            completion.append(name)
    return completion



@app.command(help="Provide train type, platform and departure times of an A -> B journey")
def journey(start: Annotated[str, typer.Option(help="Start station", autocompletion=complete_name)],
         end: Annotated[str, typer.Option(help="Stop station", autocompletion=complete_name)],
         token: Annotated[str, typer.Option(help="Token to talk with the NS API", envvar="NS_API_TOKEN")]):
    with open(STATIONS_FILE, "r") as file:
        UIC_mapping = json.load(file)
    uic_start = UIC_mapping[start]
    uic_end = UIC_mapping[end]
    print(f"Journeys from {start} -> {end}")
    with httpx.Client() as client:
        response = client.get(url=f"https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/trips?originUicCode={uic_start}&destinationUicCode={uic_end}",headers={
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': token
        })

    trips = response.json()["trips"]
    for trip in trips:
        trip = trip["legs"][0]

        if 'actualTrack' in trip['origin']:
            track = trip['origin']['actualTrack']
        elif 'plannedTrack' in trip['origin']:
            track = trip['origin']['plannedTrack']
        else:
            raise Exception("No track!")

        if 'actualDateTime' in trip['origin']:
            dep_time = datetime.strptime(trip['origin']['actualDateTime'],DATETIME_FORMAT_STRING)
            orig_dep_time = datetime.strptime(trip['origin']['plannedDateTime'],DATETIME_FORMAT_STRING)
            delay = dep_time - orig_dep_time
        elif 'plannedDateTime' in trip['origin']:
            dep_time = datetime.strptime(trip['origin']['plannedDateTime'],DATETIME_FORMAT_STRING)
            delay = timedelta(0)
        else:
            raise Exception("No departure time!")
        train_type = trip['product']['categoryCode']
        delay_minutes = int(delay.total_seconds() / 60)

        dep_string = f"{dep_time.strftime('%H:%M')}"
        if delay_minutes > 0:
             dep_string += f" +{delay_minutes}"

        time_left = dep_time - datetime.now(tz=dep_time.tzinfo)
        time_left_minutes = int(time_left.total_seconds() / 60)
        if time_left_minutes < MINUTES_NEEDED:
            continue

        print(f"{train_type} p.{track} in {time_left_minutes} min ({dep_string})")
