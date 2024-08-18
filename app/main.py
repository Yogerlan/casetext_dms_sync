from copy import deepcopy
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status

from .dms import get_files_dict

app = FastAPI()
today = datetime.today().strftime("%Y-%m-%d")


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

    since_files = get_files_dict(since)
    since_set = frozenset(since_files)
    until_files = get_files_dict(until)
    until_set = frozenset(until_files)
    sync = []

    # Create operations
    for idx in until_set - since_set:
        file = until_files[idx]
        sync.append({"op": "createFile", "file": file})

    # Delete operations
    for idx in since_set - until_set:
        file = deepcopy(since_files[idx])
        del file["name"]
        del file["meta"]
        sync.append({"op": "deleteFile", "file": file})

    # Update operations
    for idx in since_set & until_set:
        # Update FileName
        if since_files[idx]["name"] != until_files[idx]["name"]:
            file = deepcopy(until_files[idx])
            del file["meta"]
            sync.append({"op": "updateFileName", "file": file})

        # Update FileMeta
        if since_files[idx]["meta"] != until_files[idx]["meta"]:
            file = deepcopy(until_files[idx])
            del file["name"]
            sync.append({"op": "updateFileMeta", "file": file})

    return {"sync": sync}
