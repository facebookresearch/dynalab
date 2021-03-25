# Copyright (c) Facebook, Inc. and its affiliates.

import hashlib
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

    def mock_handle(self, handle_func, mock_data, mock_context):
        # Task owner can choose to override this function
        # e.g. if they have more than one input test data
        response = handle_func(mock_data, mock_context)
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

    def generate_response_signature(self, response, secret=""):
        """
        This function generates a unique signature
        based on secret, task, input and output
        """
        task, inputs, outputs = self.parse_signature_input(response)
        h = hashlib.sha1()
        my_secret = os.environ.get("my_secret", secret)
        h.update(my_secret.encode("utf-8"))
        h.update(task.encode("utf-8"))
        for key in sorted(inputs.keys()):
            h.update(str(inputs[key]).encode("utf-8"))
        for key in sorted(outputs.keys()):
            h.update(str(outputs[key]).encode("utf-8"))
        signature = h.hexdigest()
        return signature

    def sign_response(self, response):
        response["signed"] = self.generate_response_signature(response)
        return response

    @abstractmethod
    def verify_response(self, response):
        # verify the actual response
        raise NotImplementedError

    @abstractmethod
    def parse_signature_input(self, response):
        """
        Return task code name, inputs and outputs used to generate signature
        """
        raise NotImplementedError
