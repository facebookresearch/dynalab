# Copyright (c) Facebook, Inc. and its affiliates.

"""
Instructions:
Please work through this file to construct your handler. Here are things
to watch out for:
1. TODO blocks: you need to fill or modify these according to the instructions.
   The code in these blocks are for demo purpose only and they may not work.
2. NOTE inline comments: remember to follow these instructions to pass the test.
3. Please do not modify anything outside TODO blocks.
4. Only pytorch models are supported at the moment.
"""

from dynalab.handler.base_handler import BaseDynaHandler


# ############TODO############
"""
import libraries as necessrary here,
and remember to add thrid-party libraries to your requirements file
"""
import json  # noqa isort:skip
import os  # noqa isort:skip
import sys  # noqa isort:skip

import torch  # noqa isort:skip

# ############################

sys.path.append("/home/model-server/code")  # NOTE: in local test, comment this line

# ############TODO############
"""
Import modules from your own project repo here
"""
import MyModel  # noqa isort:skip

# ############################


class Handler(BaseDynaHandler):
    def initialize(self, context):
        """
        load model and extra files
        """
        model_pt_path, extra_file_dir, device = self._handler_initialize(context)

        # ############TODO############
        """
        Load model and read relevant files here.
        Your extra files can be read from os.path.join(extra_file_dir, file_name).
        """
        config = json.load(
            os.path.join(extra_file_dir, "config")
        )  # NOTE: in local test, set extra_file_dir to your actual extra file dir

        self.model = MyModel(config)
        self.model.load_state_dict(torch.load(model_pt_path, map_location="cpu"))
        self.model.to(device)
        self.model.eval()
        # ############################

        self.initialized = True

    def preprocess(self, data):
        """
        preprocess data into a format that the model can do inference on
        """
        example = self._read_data(data)

        # ############TODO############
        """
        You can extract the key and values from the input data like below
        example is a always json object. Yo can see what an example looks like by
        ```
        dynalab.tasks.{your_task}.TaskIO().get_input_json()
        ```
        """
        context = example["context"]
        hypothesis = example["hypothesis"]
        input_data = len(context) + len(hypothesis)
        # ############################

        return input_data

    def inference(self, input_data):
        """
        do inference on the processed example
        """

        # ############TODO############
        """
        Run model prediction using the processed data
        """
        with torch.no_grad():
            inference_output = self.model(input_data)
        # ############################

        return inference_output

    def postprocess(self, inference_output, data):
        """
        post process inference output into a response.
        response should be a single element list of a json
        the response format will need to pass the validation in
        ```
        dynalab.tasks.{your_task}.TaskIO().verify_response(response)
        ```
        """
        response = {}

        # ############TODO############
        """
        Add attributes to response
        """
        response["id"] = self._read_data(data)["uid"]
        response["label"] = inference_output > 0.5
        response["prob"] = inference_output
        # ############################

        return [response]


_service = Handler()


def handle(data, context):
    if not _service.initialized:
        _service.initialize(context)
    if data is None:
        return None

    # ############TODO############
    """
    Normally you don't need to change anything in this block.
    However, if you do need to change this part (e.g. function name, argument, etc.),
    remember to make corresponding changes in the Handler class definition.
    """
    input_data = _service.preprocess(data)
    output = _service.inference(input_data)
    response = _service.postprocess(output, data)
    # ############################

    return response
