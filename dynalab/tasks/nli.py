# Copyright (c) Facebook, Inc. and its affiliates.

from ts.torch_handler.base_handler import BaseHandler

from dynalab.tasks.common import BaseTaskIO


data = [
    {
        "body": {
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
            "target": 0,
        }
    }
]


class TaskIO(BaseTaskIO):
    def __init__(self):
        BaseTaskIO.__init__(self, data)

    def verify_response(self, response):
        # am example function here
        assert "prob" in response, "prob must be in response"


# To be filled
class DynaHandler(BaseHandler):
    pass
