import json
import os
from copy import deepcopy


class DMS:
    def __init__(self, since, until, testing=False):
        self.__responses_dir = os.path.join(
            os.path.dirname(__file__),
            "test-dms-responses" if testing else "dms-responses"
        )
        self.__since_files = self.__get_files(since)
        self.__until_files = self.__get_files(until)
        self.__sync_ops = []
        self.__get_create_ops()
        self.__get_delete_ops()
        self.__get_update_ops()

    def __get_files(self, date):
        files = {}
        files_path = os.path.join(self.__responses_dir, f"{date}.jsonl")

        if os.path.exists(files_path):
            with open(files_path) as f:
                for entry in f.readlines():
                    file = json.loads(entry)
                    files[file["id"]] = file

        return files

    def __get_create_ops(self):
        # Create operations
        for idx in self.__until_files.keys() - self.__since_files.keys():
            file = self.__until_files[idx]
            self.__sync_ops.append({"op": "createFile", "file": file})

    def __get_delete_ops(self):
        # Delete operations
        for idx in self.__since_files.keys() - self.__until_files.keys():
            file = deepcopy(self.__since_files[idx])
            del file["name"]
            del file["meta"]
            self.__sync_ops.append({"op": "deleteFile", "file": file})

    def __get_update_ops(self):
        # Update operations
        for idx in self.__since_files.keys() & self.__until_files.keys():
            # Update FileName
            if self.__since_files[idx]["name"] != self.__until_files[idx]["name"]:
                file = deepcopy(self.__until_files[idx])
                del file["meta"]
                self.__sync_ops.append({"op": "updateFileName", "file": file})

            # Update FileMeta
            if self.__since_files[idx]["meta"] != self.__until_files[idx]["meta"]:
                file = deepcopy(self.__until_files[idx])
                del file["name"]
                self.__sync_ops.append({"op": "updateFileMeta", "file": file})

    @property
    def sync(self):
        return self.__sync_ops
