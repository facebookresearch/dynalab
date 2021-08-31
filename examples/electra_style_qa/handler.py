# Copyright (c) Facebook, Inc. and its affiliates.

import sys

import torch
from transformers import (
    AutoConfig,
    AutoModelForQuestionAnswering,
    AutoTokenizer,
    QuestionAnsweringPipeline,
)

from dynalab.handler.base_handler import BaseDynaHandler
from dynalab.tasks.qa import TaskIO


class Handler(BaseDynaHandler):
    def initialize(self, context):
        """
        Load model and tokenizer files.
        """
        self.taskIO = TaskIO()
        model_pt_path, _, device_str = self._handler_initialize(context)
        config = AutoConfig.from_pretrained("config.json")
        device = -1 if device_str == "cpu" else int(device_str[-1])
        self.pipeline = QuestionAnsweringPipeline(
            model=AutoModelForQuestionAnswering.from_pretrained(
                model_pt_path, config=config
            ),
            tokenizer=AutoTokenizer.from_pretrained("."),
            device=device,
        )
        self.initialized = True

    def preprocess(self, data):
        """
        Preprocess data into a format that the model can do inference on.
        """
        example = self._read_data(data)
        return {"context": example["context"], "question": example["question"]}

    def inference(self, input_data):
        """
        Run model using the processed data.
        """
        result = self.pipeline(input_data)
        return result

    def postprocess(self, inference_output, data):
        """
        Post process inference output into a response.
        """
        result = inference_output
        answer = result["answer"]
        conf = result["score"]

        response = dict()
        example = self._read_data(data)
        response["id"] = example["uid"]
        response["answer"] = answer
        response["conf"] = conf
        response = self.taskIO.sign_response(response, example)
        return [response]


_service = Handler()


def handle(data, context):
    if not _service.initialized:
        _service.initialize(context)
    if data is None:
        return None
    input_data = _service.preprocess(data)
    output = _service.inference(input_data)
    response = _service.postprocess(output, data)
    return response
