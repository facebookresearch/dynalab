# Copyright (c) Facebook, Inc. and its affiliates.

import json
import os
from abc import ABC, abstractmethod

from ts.context import Context

from dynalab_cli.utils import SetupConfigHandler


class BaseTaskIO(ABC):
    # TODO: what is the best practice for a base class
    # with a mixture of abstract and concrete methods?
    def __init__(self, data):
        self.data = data

    def get_input_json(self):
        # for sending data to a serving model
        # task owner can override if there is
        # e.g. more than one input test data
        return json.dumps(self.data)

    def _get_mock_context(self, model_name):
        config_handler = SetupConfigHandler(model_name)
        config = config_handler.load_config()
        fname = os.path.basename(config["checkpoint"])
        model_dir = os.path.dirname(config["checkpoint"])
        manifest = {"model": {"serializedFile": fname}}
        context = Context(
            model_name=model_name,
            model_dir=model_dir,
            manifest=manifest,
            batch_size=1,
            gpu=False,
            mms_version=None,
        )
        return context

    def _get_mock_input_data(self):
        return [{"body": self.data}]

    def get_mock_input(self, model_name):
        # Task owner can choose to override this function
        # e.g. if they have more than one input test data
        context = self._get_mock_context(model_name)
        data = self._get_mock_input_data()
        return data, context

    def show_mock_input_data(self):
        # Task owner can choose to override this function
        # e.g. if they have more than one input test data
        print(f"Mock input data is: ", self._get_mock_input_data())

    def mock_handle(self, handle_func, data, context):
        # Task owner can choose to override this function
        # e.g. if they have more than one input test data
        response = handle_func(data, context)
        return response

    def show_model_response(self, response):
        # Task owner can choose to override this function
        # e.g. if they have more than one input test data
        print(f"Your model response is {response}")

    def verify_mock_response(self, response):
        # mock response is normally a list
        # task owner can override this function if there
        # is e.g. more than one input test data
        self.verify_response(response[0])

    @abstractmethod
    def verify_response(self, response):
        # verify the actual response
        raise NotImplementedError
