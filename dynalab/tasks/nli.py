# Copyright (c) Facebook, Inc. and its affiliates.

from ts.torch_handler.base_handler import BaseHandler

from dynalab.tasks.common import get_mock_context


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


def get_mock_input(name):
    context = get_mock_context(name)
    return data, context


# To be filled
class DynaHandler(BaseHandler):
    pass
