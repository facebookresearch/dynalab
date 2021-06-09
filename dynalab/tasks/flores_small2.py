# Copyright (c) Facebook, Inc. and its affiliates.

import uuid

from dynalab.tasks.flores_small1 import TaskIO


data = [
    {
        "uid": str(uuid.uuid4()),
        "sourceLanguage": "eng",
        "targetLanguage": "ind",
        "sourceText": "Prastawa is a great basketball player.",
    },
    {
        "uid": str(uuid.uuid4()),
        "sourceLanguage": "ind",
        "targetLanguage": "eng",
        "sourceText": "Prastawa adalah pemain basket yang hebat.",
    },
]
