# Copyright (c) Facebook, Inc. and its affiliates.

import hashlib
import json
import os
from abc import ABC, abstractmethod

from ts.context import Context

from dynalab_cli.utils import SetupConfigHandler
import requests


class BaseTaskIO(ABC):
    # TODO: what is the best practice for a base class
    # with a mixture of abstract and concrete methods?
    def __init__(self):
        pass

    def mock_handle_individually(self, model_name:str, mock_datapoints:list, handle_func):
        def _get_mock_context(model_name):
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
        mock_context = _get_mock_context(model_name)
        for data in mock_datapoints:
            print(f"Obtaining test input data ...")
            mock_data = [{"body": data}]
            print(f"Mock input data is: ", mock_data)
            print("Getting model response ...")
            response = handle_func(mock_data, mock_context)
            print(f"Your model response is {response}")
            print(f"Verifying model response ...")
            self.verify_response(response[0], data)

    def test_endpoint_individually(self, endpoint_url, json_datapoints):
        for data in json_datapoints:
            r = requests.post(endpoint_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
            try: 
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise RuntimeError(e)
            else:
                print("Test input data: ", data)
                print("Your model response: ", r.text)
                self.verify_response(r.json(), data)

    def generate_response_signature(self, response, data, secret=""):
        """
        This function generates a unique signature
        based on secret, task, input and output
        """
        task, inputs, outputs = self.parse_signature_input(response, data)
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

    def sign_response(self, response, data):
        response["signed"] = self.generate_response_signature(response, data)
        return response

    @abstractmethod
    def verify_response(self, response, data):
        """
        Defines task output by verifying a response satisfies all requirements
        """
        raise NotImplementedError

    @abstractmethod
    def parse_signature_input(self, response, data):
        """
        Return task code name, inputs and outputs used to generate signature
        """
        raise NotImplementedError
