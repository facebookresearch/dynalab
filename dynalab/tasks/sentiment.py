# Copyright (c) Facebook, Inc. and its affiliates.

import uuid

from dynalab.tasks.common import BaseTaskIO


data = {"uid": str(uuid.uuid4()), "context": "It is a good day"}


class TaskIO(BaseTaskIO):
    def __init__(self, data=data):
        BaseTaskIO.__init__(self, data)

    def verify_response(self, response):
        assert "id" in response and response["id"] == self.data["uid"]
        assert "label" in response and response["label"] in {
            "positive",
            "negative",
            "neutral",
        }
        assert response["signed"] == self.generate_response_signature(response)

    def parse_signature_input(self, response):
        task = "sentiment"
        inputs = {key: self.data[key] for key in ["context"]}
        outputs = {key: response[key] for key in ["label"]}
        return task, inputs, outputs
