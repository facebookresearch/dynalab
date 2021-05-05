# Copyright (c) Facebook, Inc. and its affiliates.

import uuid

from dynalab.tasks.common import BaseTaskIO


data = {"uid": str(uuid.uuid4()), "statement": "It is a good day"}


class TaskIO(BaseTaskIO):
    def __init__(self, data=data):
        BaseTaskIO.__init__(self, data)

    def verify_response(self, response):
        """
        Expected response format:
        {
            "id": copy from input["uid"],
            "label": "hate" | "nothate",
            "prob": {"hate": 0.2, "nothate": 0.8} # optional, a dictionary of probabilities
            (0~1) for each label, will be normalized on our side
        }
        """
        # required keys 
        assert "id" in response and response["id"] == self.data["uid"]
        assert "label" in response and response["label"] in {"hate", "nothate"}
        assert response["signed"] == self.generate_response_signature(response)
        Nk = 3
        # optional keys 
        if "prob" in response:
            assert self._verify_prob(response["prob"])
            Nk += 1
        assert Nk == len(response), f"response should not contain other extra keys"

    def _verify_prob(self, prob):
        error_message = (
            "response['prob'] should be dictionary like {'hate': 0.2, 'nothate': 0.8}"
        )
        assert isinstance(prob, dict), error_message
        assert len(prob) == 2 and "hate" in prob and "nothate" in prob, error_message
        for key in prob:
            assert (
                prob[key] >= 0 and prob[key] <= 1
            ), f"Probability for label {key} should be between 0 and 1"
        return True

    def parse_signature_input(self, response):
        task = "hs"
        inputs = {key: self.data[key] for key in ["statement"]}
        outputs = {key: response[key] for key in ["label"]}
        return task, inputs, outputs
