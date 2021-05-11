# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

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
