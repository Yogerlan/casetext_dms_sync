import os
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status

from .dms import DMS
from .schemas import PingResponse, SyncResponse

today = datetime.today().strftime("%Y-%m-%d")
yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

app = FastAPI(
    title="DMS-CaseText Sync MSV",
    summary="DMS-CaseText sync operation list generator microservice",
    description="Keeps customers' research content synced with their provided third-party DMS content, "
    "by generating the required Research Service operations at some time range.",
    license_info={
        "name": "MIT License",
        "identifier": "MIT"
    }
)


@app.get(
    "/ping",
    summary="An ancient game",
    description="Challenge the server for a match.",
    response_description="A server response message.",
    response_model=PingResponse
)
async def ping():
    return {"msg": "pong"}


@app.get(
    "/sync",
    summary="Generates a sync operation list",
    description="Given the file lists of the DMS on two dates, "
    "an operation list is generated for the Research Service to sync its customers' content.",
    response_description="A list of file operations.",
    response_model=list[SyncResponse],
    response_model_exclude_none=True
)
async def sync_operations(
    since: Annotated[str, Query(
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        title="Since",
        description="Sync starting date."
    )] = yesterday,
    until: Annotated[str, Query(
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        title="Until",
        description="Sync ending date."
    )] = today
):
    # Prevent nonsense dates.
    try:
        datetime.fromisoformat(since)
        datetime.fromisoformat(until)
    except ValueError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Okay, Houston ... we've had a problem here. Which extraterrestrial calendar is that date from?"
        )

    # Prevent future dates.
    if since > today or until > today:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="I can't wait to see Back to the Future 4. It was pretty good!"
        )

    # Prevent switch dates order.
    if since > until:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="I am inevitable. And I... am... Iron Man."
        )

    dms = DMS(since, until, os.getenv("TESTING") is not None)

    return dms.sync
