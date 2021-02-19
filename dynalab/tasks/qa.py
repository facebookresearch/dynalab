# Copyright (c) Facebook, Inc. and its affiliates.

from dynalab.tasks.common import BaseTaskIO


data = {
    "answer": "pretend you are reviewing a place",
    "context": "Please pretend you are reviewing a place, " + "product, book or movie",
    "hypothesis": "What should i pretend?",
}


class TaskIO(BaseTaskIO):
    def __init__(self):
        BaseTaskIO.__init__(self, data)

    def verify_response(self, response):
        # am example function here
        assert "prob" in response
