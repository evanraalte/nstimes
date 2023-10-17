import os
from datetime import datetime

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from pydantic_settings import BaseSettings
from slowapi import _rate_limit_exceeded_handler
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from nstimes.departure import Departure
from nstimes.departure import get_departures
from nstimes.utils import convert_to_rfc3339
from nstimes.utils import get_uic_mapping


class Settings(BaseSettings):  # type: ignore[misc]
    virtual_host: str = ""
    ns_api_token: str = ""

def get_settings() -> Settings:
    return Settings()

load_dotenv()
limiter = Limiter(key_func=get_remote_address)
settings = Settings()


def get_app(limiter: Limiter, settings: Settings) -> FastAPI:
    print(settings)
    if settings.virtual_host:
        print("Rolling out production environment")
        servers = [
            {
                "url": f"https://{settings.virtual_host}/",
                "description": "Production environment",
            }
        ]
        docs_url = None  # No docs for production environment
    else:
        print("Rolling out local environment")
        servers = [
            {"url": "http://localhost:8000/", "description": "Local environment"}
        ]
        docs_url = "/docs"

    app = FastAPI(servers=servers, docs_url=docs_url)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return app


app = get_app(limiter, settings)


@app.get("/stations")
@limiter.limit(limit_value="5/minute")
async def stations(request: Request) -> dict[str, str]:
    return get_uic_mapping()


@app.get("/journey")
async def journey(
    start: str,
    end: str,
    settings: Settings = Depends(get_settings),
    date: str = datetime.now().strftime("%d-%m-%Y"),
    time: str = datetime.now().strftime("%H:%M"),
) -> list[Departure]:
    rdc3339_datetime = convert_to_rfc3339(time, date)
    if not settings.ns_api_token:
        raise HTTPException(status_code=500, detail=f"Could not find NS_API_TOKEN")
    try:
        departures = get_departures(
            start=start,
            end=end,
            token=settings.ns_api_token,
            rdc3339_datetime=rdc3339_datetime,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"One or more stations not correct: {exc}, get available stations from /stations",
        )
    return departures


def start() -> None:
    """Launched with `poetry run start` at root level"""
    uvicorn.run("nstimes.server:app", host="0.0.0.0", port=8000)  # pragma: no cover


if __name__ == "__main__":
    start()  # pragma: no cover
