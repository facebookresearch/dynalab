# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import hashlib
import json
import os
from abc import ABC, abstractmethod

import requests
from ts.context import Context

from dynalab_cli.utils import SetupConfigHandler


class BaseTaskIO(ABC):
    # TODO: what is the best practice for a base class
    # with a mixture of abstract and concrete methods?
    def __init__(self):
        pass

    def _get_mock_context(self, model_name: str, use_gpu: bool):
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
            gpu=None,
            mms_version=None,
        )
        return context

    def mock_handle_individually(
        self, model_name: str, mock_datapoints: list, use_gpu: bool, handle_func
    ):
        mock_context = self._get_mock_context(model_name, use_gpu)
        N = len(mock_datapoints)
        for i, data in enumerate(mock_datapoints):
            print(f"Test data {i+1} / {N}")
            print(f"Mock input data is: ", data)
            mock_data = [{"body": data}]
            print("Getting model response ...")
            responses = handle_func(mock_data, mock_context)
            assert len(responses) == 1, "The model should return one torchserve sample !"
            response = responses[0]
            print(f"Your model response is {response}")
            if isinstance(response, str):
                # Model can return either dict or string. Torchserve will handle serialization.
                try:
                    response = json.loads(response)
                except Exception as e:
                    raise RuntimeError("The model response isn't valid json !") from e
            else:
                try:
                    json.dumps(response)
                except Exception as e:
                    raise RuntimeError(
                        "The model response isn't serializable to json !"
                    ) from e
            print(f"Verifying model response ...")
            self.verify_response(response, data)

    def mock_handle_with_batching(
        self, model_name: str, mock_datapoints: list, use_gpu: bool, handle_func
    ):
        mock_context = self._get_mock_context(model_name, use_gpu)
        N = len(mock_datapoints)
        mock_data = [
            {
                "body": "\n".join(
                    json.dumps(sample, ensure_ascii=False) for sample in mock_datapoints
                )
            }
        ]
        print("Getting model response ...")
        responses = handle_func(mock_data, mock_context)
        assert len(responses) == 1, "The model should return one torchserve sample !"

        try:
            responses = [json.loads(r) for r in responses[0].splitlines()]
        except Exception as e:
            raise RuntimeError("The model response isn't serializable to json !") from e

        for i, (data, response) in enumerate(zip(mock_datapoints, responses)):
            print(f"Test data {i+1} / {N}")
            print(f"Mock input data is: ", data)
            print(f"Your model response is {response}")
            print(f"Verifying model response ...")
            self.verify_response(response, data)

    def test_endpoint_individually(self, endpoint_url, json_datapoints):
        N = len(json_datapoints)
        for i, data in enumerate(json_datapoints):
            print(f"Test data {i+1} / {N}")
            print("Test input data: ", data)
            r = requests.post(
                endpoint_url,
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
            )
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print("Inference failed")
                raise RuntimeError(f"Inference failed: {e}")
            else:
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
