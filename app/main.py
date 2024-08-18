import os
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status

from .dms import DMS

today = datetime.today().strftime("%Y-%m-%d")
app = FastAPI()


@app.get("/ping")
async def ping():
    return {"msg": "pong"}


@app.get("/sync")
async def sync_operations(
    since: Annotated[str, Query(
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )],
    until: Annotated[str, Query(
        pattern=r"^\d{4}-\d{2}-\d{2}$"
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
