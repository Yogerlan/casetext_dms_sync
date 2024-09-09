import json
import os
from copy import deepcopy
from hashlib import sha1

from motor.motor_asyncio import AsyncIOMotorClient


class DMS:
    def __init__(self, testing: bool = False, docker: bool = False) -> None:
        host = "db" if docker else "localhost"
        client = AsyncIOMotorClient(f"mongodb://{host}:27017")

        if testing:
            self.__responses_dir = os.path.join(
                os.path.dirname(__file__), "test-dms-responses"
            )
            self.__collection = client.dms_test.files
        else:
            self.__responses_dir = os.path.join(
                os.path.dirname(__file__), "dms-responses"
            )
            self.__collection = client.dms.files

    async def store_documents(self) -> None:
        dates = sorted([d.split(".")[0]
                        for d in os.listdir(self.__responses_dir)])
        files = {}

        for date in dates:
            chunk = await self.__get_files(date, False)

            # update until dates
            for key in chunk.keys() & files.keys():
                files[key].update({"until": date})

            # add new files
            for key in chunk.keys() - files.keys():
                files[key] = chunk[key]
                files[key].update({"since": date, "until": date})

        if len(files):
            await self.__collection.insert_many(list(files.values()))

    async def clean_documents(self) -> None:
        await self.__collection.delete_many({})

    async def get_ops(self, since: str, until: str) -> list:
        self.__since_files = await self.__get_files(since)
        self.__until_files = await self.__get_files(until)
        self.__sync_ops = []
        self.__get_create_ops()
        self.__get_delete_ops()
        self.__get_update_ops()

        return self.__sync_ops

    async def __get_files(self, date: str, from_db: bool = True) -> dict:
        files = {}

        if from_db:
            records = self.__collection.find(
                {"since": {"$lte": date}, "until": {"$gte": date}},
                {"_id": 0, "since": 0, "until": 0}
            )

            async for record in records:
                files[record["id"]] = record
        else:
            files_path = os.path.join(self.__responses_dir, f"{date}.jsonl")

            if os.path.exists(files_path):
                with open(files_path) as f:
                    for entry in f.readlines():
                        file = json.loads(entry)
                        idx = sha1(json.dumps(file).encode()).hexdigest()
                        files[idx] = file

        return files

    def __get_create_ops(self) -> None:
        # Create operations
        for idx in self.__until_files.keys() - self.__since_files.keys():
            file = self.__until_files[idx]
            self.__sync_ops.append({"op": "createFile", "file": file})

    def __get_delete_ops(self) -> None:
        # Delete operations
        for idx in self.__since_files.keys() - self.__until_files.keys():
            file = deepcopy(self.__since_files[idx])
            file["name"] = None
            file["meta"] = None
            self.__sync_ops.append({"op": "deleteFile", "file": file})

    def __get_update_ops(self) -> None:
        # Update operations
        for idx in self.__since_files.keys() & self.__until_files.keys():
            # Update FileName
            if self.__since_files[idx]["name"] != self.__until_files[idx]["name"]:
                file = deepcopy(self.__until_files[idx])
                file["meta"] = None
                self.__sync_ops.append({"op": "updateFileName", "file": file})

            # Update FileMeta
            if self.__since_files[idx]["meta"] != self.__until_files[idx]["meta"]:
                file = deepcopy(self.__until_files[idx])
                file["name"] = None
                self.__sync_ops.append({"op": "updateFileMeta", "file": file})
