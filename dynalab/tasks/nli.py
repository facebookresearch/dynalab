# Copyright (c) Facebook, Inc. and its affiliates.

import uuid

from dynalab.tasks.common import BaseTaskIO


data = [
    {
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
    },
    {
        "uid": str(uuid.uuid4()),
        "context": "Another test point with utf-8, hackamore "
        + "from j?\u00a1quima; mustang from mestengo",
        "hypothesis": "See how it works",
    },
    # {
    #     "uid": str(uuid.uuid4()),
    #     "context": " ".join([str(x) + "_" for x in range(513)]),
    #     "hypothesis": "Hope you can handle this length",
    # },
]


class TaskIO(BaseTaskIO):
    def __init__(self):
        BaseTaskIO.__init__(self)

    def verify_response(self, response, data):
        """
        Expected response format:
        {
            "id": copy from input["uid"],
            "label": "c" | "e" | "n",
            "prob": {"c": 0.2, "e": 0.6, "n": 0.2} # optional, a dictionary of
            probabilities (0~1) for each label, will be normalized on our side
        }
        """
        # required keys
        assert "id" in response and response["id"] == data["uid"]
        assert "label" in response and response["label"] in {"c", "e", "n"}
        assert response["signed"] == self.generate_response_signature(response, data)
        Nk = 3
        # optional keys
        if "prob" in response:
            assert self._verify_prob(response["prob"])
            Nk += 1
        assert Nk == len(response), f"response should not contain other extra keys"

    def _verify_prob(self, prob):
        error_message = (
            "response['prob'] should be dictionary like {'c': 0.1, 'e': 0.3. 'n': 0.6}"
        )
        assert isinstance(prob, dict), error_message
        assert (
            len(prob) == 3 and "c" in prob and "e" in prob and "n" in prob
        ), error_message
        for key in prob:
            assert (
                prob[key] >= 0 and prob[key] <= 1
            ), f"Probability for label {key} should be between 0 and 1"
        return True

    def parse_signature_input(self, response, data):
        task = "nli"
        inputs = {key: data[key] for key in ["context", "hypothesis"]}
        outputs = {key: response[key] for key in ["label"]}
        return task, inputs, outputs
