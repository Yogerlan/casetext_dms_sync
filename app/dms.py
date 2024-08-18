import json
import os

RESPONSES_DIR = os.path.join(os.path.dirname(__file__), "dms-responses")


def get_files_dict(date: str):
    files_dict = {}
    files_path = os.path.join(RESPONSES_DIR, f"{date}.jsonl")

    if os.path.exists(files_path):
        with open(files_path) as f:
            for entry in f.readlines():
                file = json.loads(entry)
                files_dict[file["id"]] = file

    return files_dict
