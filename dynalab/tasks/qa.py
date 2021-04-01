# Copyright (c) Facebook, Inc. and its affiliates.

import uuid

from dynalab.tasks.common import BaseTaskIO


data = {
    "uid": str(uuid.uuid(4)),
    "context": "Please pretend you are reviewing a place, " + "product, book or movie",
    "question": "What should i pretend?",
}


class TaskIO(BaseTaskIO):
    def __init__(self, data=data):
        BaseTaskIO.__init__(self, data)

    def verify_response(self, response):
        assert "id" in response and response["id"] == self.data["uid"]
        assert "answer" in response and response["answer"] in self.data["context"]
        assert response["signed"] == self.generate_response_signature(response)

    def parse_signature_input(self, response):
        task = "qa"
        inputs = {key: self.data[key] for key in ["context", "question"]}
        outputs = {key: response[key] for key in ["answer"]}
        return task, inputs, outputs
