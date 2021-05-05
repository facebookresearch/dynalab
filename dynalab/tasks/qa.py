# Copyright (c) Facebook, Inc. and its affiliates.

import uuid

from dynalab.tasks.common import BaseTaskIO


data = {
    "uid": str(uuid.uuid4()),
    "context": "Please pretend you are reviewing a place, " + "product, book or movie",
    "question": "What should i pretend?",
}


class TaskIO(BaseTaskIO):
    def __init__(self, data=data):
        BaseTaskIO.__init__(self, data)

    def verify_response(self, response):
        """
        Expected response format:
        {
            "id": copy from input["uid"],
            "answer": the answer string extracted from input["context"],
            "conf": <a float between 0 and 1> # optional, the model's confidence score
            of the given answer; a recommended way of computing this is the product of
            the probabilities corresponding to the answer span start and end indices,
            obtained by a softmax over span start logits, and a separate softmax over
            span end logits
        }
        """
        assert "id" in response and response["id"] == self.data["uid"]
        assert "answer" in response and response["answer"] in self.data["context"]
        assert response["signed"] == self.generate_response_signature(response)
        Nk = 3
        if "conf" in response:
            assert (
                response["conf"] >= 0 and response["conf"] <= 1
            ), "Confidence score should be between 0 and 1"
            Nk += 1
        assert Nk == len(response), f"response should not contain other extra keys"

    def parse_signature_input(self, response):
        task = "qa"
        inputs = {key: self.data[key] for key in ["context", "question"]}
        outputs = {key: response[key] for key in ["answer"]}
        return task, inputs, outputs
