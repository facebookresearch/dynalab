# Copyright (c) Facebook, Inc. and its affiliates.

import uuid

from dynalab.tasks.common import BaseTaskIO


data = {
    "uid": str(uuid.uuid4()),
    "context": "Old Trafford is a football stadium "
    + " in Old Trafford, "
    + "Greater Manchester, England, and the home of "
    + "Manchester United. "
    + "With a capacity of 75,643, it is the largest club football "
    + "stadium in the United Kingdom, the second-largest football "
    + "stadium, and the eleventh-largest in Europe. "
    + "It is about 0.5 mi from Old Trafford Cricket Ground"
    + " and the adjacent tram stop.",
    "hypothesis": "There is no club football stadium in "
    + "England larger "
    + "than the one in Manchester.",
}


class TaskIO(BaseTaskIO):
    def __init__(self, data=data):
        BaseTaskIO.__init__(self, data)

    def verify_response(self, response):
        assert "id" in response and response["id"] == self.data["uid"]
        assert "label" in response and response["label"] in {"c", "e", "n"}
        assert response["signed"] == self.generate_response_signature(response)

    def parse_signature_input(self, response):
        task = "nli"
        inputs = {key: self.data[key] for key in ["context", "hypothesis"]}
        outputs = {key: response[key] for key in ["label"]}
        return task, inputs, outputs
