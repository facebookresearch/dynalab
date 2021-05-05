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

    def get_input_json_single(self):
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

    def mock_handle_single(self, model_name, handle_func):
        mock_context = self._get_mock_context(model_name)
        print(f"Obtaining test input data ...")
        mock_data = [{"body": self.data}]
        print(f"Mock input data is: ", mock_data)
        print("Getting model response ...")
        response = handle_func(mock_data, mock_context)
        print(f"Your model response is {response}")
        print(f"Verifying model response ...")
        self.verify_response(response[0])
        return response

    def generate_response_signature(self, response, secret=""):
        """
        This function generates a unique signature
        based on secret, task, input and output
        """
        task, inputs, outputs = self.parse_signature_input(response)
        h = hashlib.sha1()
        my_secret = os.environ.get("MY_SECRET", secret)
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
        """
        Defines task output by verifying a response satisfies all requirements
        """
        raise NotImplementedError

    @abstractmethod
    def parse_signature_input(self, response):
        """
        Return task code name, inputs and outputs used to generate signature
        """
        raise NotImplementedError
