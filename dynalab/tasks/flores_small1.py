# Copyright (c) Facebook, Inc. and its affiliates.

import uuid

from dynalab.tasks.common import BaseTaskIO


data = [
    {
        "uid": str(uuid.uuid4()),
        "sourceLanguage": "eng",
        "targetLanguage": "hrv",
        "sourceText": "Toni Kukoč is a great basketball player.",
    },
    {
        "uid": str(uuid.uuid4()),
        "sourceLanguage": "hrv",
        "targetLanguage": "eng",
        "sourceText": "Toni Kukoč sjajan je košarkaš.",
    },
]


class TaskIO(BaseTaskIO):
    def __init__(self):
        BaseTaskIO.__init__(self)

    def verify_response(self, response, data):
        assert response.keys() == {"id", "translatedText", "signed"}, response.keys()
        assert response["id"] == data["uid"]
        assert isinstance(response["translatedText"], str)
        assert response["signed"] == self.generate_response_signature(response, data)

    def parse_signature_input(self, response, data):
        task = "flores"
        inputs = {
            key: data[key] for key in ["sourceLanguage", "targetLanguage", "sourceText"]
        }
        outputs = {key: response[key] for key in ["translatedText"]}
        return task, inputs, outputs
