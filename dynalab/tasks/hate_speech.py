# Copyright (c) Facebook, Inc. and its affiliates.

from ts.torch_handler.base_handler import BaseHandler

from dynalab.tasks.common import BaseTaskIO


data = [
    {
        "body": {
            "context": "Please provide a hateful or not hateful statement",
            "hypothesis": "It is a good day",
            "target": 0,
        }
    }
]


class TaskIO(BaseTaskIO):
    def __init__(self):
        BaseTaskIO.__init__(self, data)

    def verify_response(self, response):
        # am example function here
        assert "prob" in response


# To be filled
class DynaHandler(BaseHandler):
    pass
