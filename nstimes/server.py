import os
from datetime import datetime

import typer
import uvicorn
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException

from nstimes.departure import Departure
from nstimes.departure import get_departures
from nstimes.utils import convert_to_rfc3339

app = FastAPI()


def get_token() -> str:
    try:
        return os.environ["NS_API_TOKEN"]
    except KeyError:
        raise HTTPException(status_code=500, detail=f"Could not find NS_API_TOKEN")


@app.get("/journey")
async def journey(
    start: str,
    end: str,
    token: str = Depends(get_token),
    date: str = datetime.now().strftime("%d-%m-%Y"),
    time: str = datetime.now().strftime("%H:%M"),
) -> list[Departure]:
    rdc3339_datetime = convert_to_rfc3339(time, date)
    departures = get_departures(
        start=start,
        end=end,
        token=token,
        rdc3339_datetime=rdc3339_datetime,
    )
    return departures


def start() -> None:
    """Launched with `poetry run start` at root level"""
    uvicorn.run("nstimes.server:app", host="0.0.0.0", port=8000)  # pragma: no cover
