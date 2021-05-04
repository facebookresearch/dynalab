# Copyright (c) Facebook, Inc. and its affiliates.

import uuid

from dynalab.tasks.common import BaseTaskIO


data = {
    "uid": str(uuid.uuid4()),
    "source_language": "en_XX",
    "target_language": "hr_HR",
    "source_text": "Hello world !",
}


class TaskIO(BaseTaskIO):
    def __init__(self, data=data):
        BaseTaskIO.__init__(self, data)

    def verify_response(self, response):
        assert "id" in response and response["id"] == self.data["uid"]
        assert "translated_text" in response and isinstance(response["translated_text"], str)
        assert response["signed"] == self.generate_response_signature(response)

    def parse_signature_input(self, response):
        task = "flores"
        inputs = {key: self.data[key] for key in ["source_language", "target_language", "source_text"]}
        outputs = {key: response[key] for key in ["translated_text"]}
        return task, inputs, outputs
