# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import hashlib
import json
import os
import uuid

import requests
from ts.context import Context

from dynalab_cli.utils import SetupConfigHandler
from dynalab.tasks.io_mock_data import io_mock_data
from dynalab.tasks.io_verifiers import io_type_verifiers


class TaskIO:

    def __init__(self, task_info_path):
        if os.path.exists(task_info_path):
            with open(task_info_path) as f:
                self.task_info = json.load(f)
        else:
            raise RuntimeError(
                f"No task io found. Please call dynalab-cli init to initiate this repo."
            )

        self.task_info_path = task_info_path
        self.mock_datapoints = self.initialize_mock_data()

    def initialize_mock_data(self):

        type_to_data_dict = dict()
        max_mock_data_len = 0

        def load_mock_data_for_io_types(io_types, max_mock_data_len_inner):
            for io_type in io_types:
                def_type = io_type["type"]
                if def_type not in type_to_data_dict:
                    type_to_data_dict[def_type] = io_mock_data[def_type]
                max_mock_data_len_inner = max(max_mock_data_len_inner, len(type_to_data_dict[def_type]))

            return max_mock_data_len_inner

        max_mock_data_len = load_mock_data_for_io_types(self.task_info["io_def"]["input"], max_mock_data_len)
        max_mock_data_len = load_mock_data_for_io_types(self.task_info["io_def"]["context"], max_mock_data_len)

        mock_data = []

        def add_mock_data_for_io_types(io_types, datum):
            for io_type in io_types:
                data_for_input_type = type_to_data_dict[io_type["type"]]
                datum[io_type["name"]] = data_for_input_type[i % len(data_for_input_type)]

        for i in range(max_mock_data_len):
            datum = {
                "uid": str(uuid.uuid4())
            }
            add_mock_data_for_io_types(self.task_info["io_def"]["input"], datum)
            add_mock_data_for_io_types(self.task_info["io_def"]["context"], datum)
            mock_data.append(datum)

        return mock_data

    @staticmethod
    def _get_mock_context(model_name: str, use_gpu: bool):
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
        self, model_name: str, use_gpu: bool, handle_func
    ):
        mock_context = TaskIO._get_mock_context(model_name, use_gpu)
        N = len(self.mock_datapoints)
        for i, data in enumerate(self.mock_datapoints):
            print(f"Test data {i+1} / {N}")
            print(f"Mock input data is: ", data)
            mock_data = [{"body": data}]
            print("Getting model response ...")
            responses = handle_func(mock_data, mock_context, self.task_info_path)
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
        self, model_name: str, use_gpu: bool, handle_func
    ):
        mock_context = TaskIO._get_mock_context(model_name, use_gpu)
        N = len(self.mock_datapoints)
        mock_data = [
            {
                "body": "\n".join(
                    json.dumps(sample, ensure_ascii=False) for sample in self.mock_datapoints
                )
            }
        ]
        print("Getting model response ...")
        responses = handle_func(mock_data, mock_context, self.task_info_path)
        assert len(responses) == 1, "The model should return one torchserve sample !"

        try:
            responses = [json.loads(r) for r in responses[0].splitlines()]
        except Exception as e:
            raise RuntimeError("The model response isn't serializable to json !") from e

        for i, (data, response) in enumerate(zip(self.mock_datapoints, responses)):
            print(f"Test data {i+1} / {N}")
            print(f"Mock input data is: ", data)
            print(f"Your model response is {response}")
            print(f"Verifying model response ...")
            self.verify_response(response, data)

    def test_endpoint_individually(self, endpoint_url):
        N = len(self.mock_datapoints)
        for i, data in enumerate(self.mock_datapoints):
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
        response["signature"] = self.generate_response_signature(response, data)

    def verify_response(self, response, data):
        """
        Defines task output by verifying a response satisfies all requirements
        """
        assert len(response) == 3
        assert "id" in response and response["id"] == data["uid"]
        assert response["signature"] == self.generate_response_signature(response, data)

        model_response = response["model_response"]
        targets = self.task_info["io_def"]["target"]

        missing_target_fields = len(targets)
        extra_fields = len(model_response)

        target_names = [target["name"] for target in targets]

        outputs = self.task_info["io_def"]["output"]
        name_to_constructor_args = {}
        for output in outputs:
            name_to_constructor_args[output["name"]] = output["constructor_args"]

        for output in outputs:
            output_name = output["name"]
            if output_name in model_response:
                extra_fields -= 1
                if output_name in target_names:
                    missing_target_fields -= 1

                io_type_verifiers[output["type"]](
                    model_response[output_name],
                    name_to_constructor_args[output_name],
                    name_to_constructor_args,
                    data
                )

        assert missing_target_fields == 0
        assert extra_fields == 0

    def parse_signature_input(self, response, data):
        """
        Return task code name, inputs and outputs used to generate signature
        """

        task = self.task_info["task"]

        def add_io_types(io_types, container_obj, value_src):
            for io_type in io_types:
                name = io_type["name"]
                container_obj[name] = value_src[name]

        inputs, outputs = dict(), dict()

        add_io_types(self.task_info["io_def"]["input"], inputs, data)
        add_io_types(self.task_info["io_def"]["context"], inputs, data)
        add_io_types(self.task_info["io_def"]["output"], outputs, response["model_response"])

        return task, inputs, outputs
