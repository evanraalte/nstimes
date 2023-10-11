from datetime import datetime, timedelta
import os
import typer
from typing_extensions import Annotated
import httpx
import json
from importlib.metadata import version
from rich import print
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

DATETIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%S%z"
MINUTES_NEEDED = 0
SCRIPT_DIR = os.path.dirname(__file__)
STATIONS_FILE = os.path.join(SCRIPT_DIR,"stations.json")

app = typer.Typer(
    help="Find your next train home while you are in CLI. I used the Dutch Railway Services (Nederlandse Spoorwegen) API to make myself this tool.",
    pretty_exceptions_show_locals=os.getenv("SHOW_LOCALS"),
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
        with open(STATIONS_FILE, 'w', encoding="utf-8") as file:
            json.dump(UIC_mapping, file)
    return UIC_mapping

def complete_name(incomplete: str):
    completion = []
    with open(STATIONS_FILE, "r",encoding="utf-8") as file:
        uic_mapping = json.load(file)
    for name in uic_mapping:
        if name.startswith(incomplete):
            completion.append(name)
    return completion



@app.command(help="Provide train type, platform and departure times of an A -> B journey")
def journey(start: Annotated[str, typer.Option(help="Start station", shell_complete=complete_name)],
         end: Annotated[str, typer.Option(help="Stop station", shell_complete=complete_name)],
         token: Annotated[str, typer.Option(help="Token to talk with the NS API", envvar="NS_API_TOKEN")]):
    with open(STATIONS_FILE, "r",encoding="utf-8") as file:
        uic_mapping = json.load(file)
    uic_start = uic_mapping[start]
    uic_end = uic_mapping[end]
    print(f"Journeys from {start} -> {end}")
    with httpx.Client() as client:
        response = client.get(url=f"https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/trips?originUicCode={uic_start}&destinationUicCode={uic_end}",headers={
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': token
        })
        if response.status_code != 200:
            typer.Exit(1)
    trips = response.json()["trips"]
    for trip in trips:
        trip = trip["legs"][0]

        if 'actualTrack' in trip['origin']:
            track = trip['origin']['actualTrack']
        elif 'plannedTrack' in trip['origin']:
            track = trip['origin']['plannedTrack']
        else:
            track = "?"

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
        time_left = dep_time - datetime.now(tz=dep_time.tzinfo)
        time_left_minutes = int(time_left.total_seconds() / 60)


        if time_left_minutes < MINUTES_NEEDED:
            continue

        dep_string = f"{dep_time.strftime('%H:%M')}"
        if delay_minutes > 0:
             dep_string = f"[bold red]{dep_string}[/bold red]"
             time_left_minutes = f"[bold red]{time_left_minutes}[/bold red]"

        print(f"{train_type} p.{track} in {time_left_minutes} min ({dep_string})")

def version_callback(value: bool):
    if value:
        print(f"nstimes version: {version(__package__)}")
        raise typer.Exit()

@app.callback()
def main(
    version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True),
):
    return
