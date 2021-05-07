# Copyright (c) Facebook, Inc. and its affiliates.

import uuid

from dynalab.tasks.common import BaseTaskIO


data = [
    {"uid": str(uuid.uuid4()), "statement": "It is a good day"},
    {
        "uid": str(uuid.uuid4()),
        "statement": "Let's try a utf-8 like hackamore from j?\u00a1quima;",
    },
    {
        "uid": str(uuid.uuid4()),
        "statement": " ".join([str(x) + "_" for x in range(513)]),
    },
]


class TaskIO(BaseTaskIO):
    def __init__(self):
        BaseTaskIO.__init__(self)

    def verify_response(self, response, data):
        """
        Expected response format:
        {
            "id": copy from input["uid"],
            "label": "hateful" | "not-hateful",
            "prob": {"hateful": 0.2, "not-hateful": 0.8} # optional, 
            a dictionary of probabilities (0~1) for each label, 
            will be normalized on our side
        }
        """
        # required keys
        assert "id" in response and response["id"] == data["uid"]
        assert "label" in response and response["label"] in {"hateful", "not-hateful"}
        assert response["signed"] == self.generate_response_signature(response, data)
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
        assert len(prob) == 2 and "hateful" in prob and "not-hateful" in prob, error_message
        for key in prob:
            assert (
                prob[key] >= 0 and prob[key] <= 1
            ), f"Probability for label {key} should be between 0 and 1"
        return True

    def parse_signature_input(self, response, data):
        task = "hs"
        inputs = {key: data[key] for key in ["statement"]}
        outputs = {key: response[key] for key in ["label"]}
        return task, inputs, outputs
