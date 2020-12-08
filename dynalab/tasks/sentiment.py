# Copyright (c) Facebook, Inc. and its affiliates.

from ts.torch_handler.base_handler import BaseHandler

from dynalab.tasks.common import get_mock_context


data = [
    {
        "body": {
            "context": "Please pretend you a reviewing a place, "
            + "product, book or movie.",
            "hypothesis": "It is a good day",
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
