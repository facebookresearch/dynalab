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
            "confidence": <a float between 0 and 1> # the model's confidence score of the given answer; a recommended way of computing this is the product of the starting and end index, obtained by softmax across all starting and end index respectively
        }
        """
        assert "id" in response and response["id"] == self.data["uid"]
        assert "answer" in response and response["answer"] in self.data["context"]
        assert "confidence" in response and response["confidence"] >= 0 and response["confidence"] <= 1. "Confidence score should be between 0 and 1"
        assert response["signed"] == self.generate_response_signature(response)
        assert len(response) == 4, f"response should not contain other extra keys"
    
    def parse_signature_input(self, response):
        task = "qa"
        inputs = {key: self.data[key] for key in ["context", "question"]}
        outputs = {key: response[key] for key in ["answer"]}
        return task, inputs, outputs
