import json
import os
from datetime import datetime

import httpx
import typer


SCRIPT_DIR = os.path.dirname(__file__)
STATIONS_FILE = os.path.join(SCRIPT_DIR, "stations.json")
DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%H:%M"


def get_uic_mapping() -> dict[str, str]:
    with open(STATIONS_FILE, "r", encoding="utf-8") as file:
        uic_mapping: dict[str, str] = json.load(file)
    return uic_mapping


def get_headers(token: str) -> dict[str, str]:
    return {"Cache-Control": "no-cache", "Ocp-Apim-Subscription-Key": token}


def httpx_get(token: str, query_params: dict[str, str], api: str) -> httpx.Response:
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


def convert_to_rfc3339(time: str, date: str) -> str:
    datetime_obj = datetime.strptime(f"{date} {time}", f"{DATE_FORMAT} {TIME_FORMAT}")
    rfc3339_str = datetime_obj.isoformat()
    return rfc3339_str
