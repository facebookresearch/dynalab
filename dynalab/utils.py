# Copyright (c) Facebook, Inc. and its affiliates.

from typing import List

import requests

from dynalab.config import DYNABENCH_API


def list_datasets() -> List[str]:
    tasks_url = f"{DYNABENCH_API}/tasks"
    response = requests.get(tasks_url)
    response = response.json()

    ids: List[str] = []

    for item in response:
        ids.append(item["shortname"])

    return sorted(ids)
