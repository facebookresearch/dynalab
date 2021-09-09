# Copyright (c) Facebook, Inc. and its affiliates.

import torch
from transformers import AutoConfig, AutoModelForQuestionAnswering, AutoTokenizer

from dynalab.handler.base_handler import BaseDynaHandler
from dynalab.tasks.task_io import TaskIO


class Handler(BaseDynaHandler):
    def initialize(self, context):
        """
        Load model and tokenizer files.
        """

        self.taskIO = TaskIO("qa")
        model_pt_path, _, device_str = self._handler_initialize(context)
        config = AutoConfig.from_pretrained("config.json")
        self.model = AutoModelForQuestionAnswering.from_pretrained(
            model_pt_path, config=config
        )
        self.tokenizer = AutoTokenizer.from_pretrained(".")
        self.model.to(torch.device(device_str))
        self.model.eval()

        self.initialized = True

    def preprocess(self, data):
        """
        Preprocess data into a format that the model can do inference on.
        """
        example = self._read_data(data)
        context = example["context"]
        question = example["question"]
        input_encoding = self.tokenizer.encode_plus(
            question, context, max_length=512, return_tensors="pt"
        )
        input_ids = input_encoding["input_ids"].tolist()[0]

        return (input_encoding, input_ids)

    def inference(self, input_data):
        """
        Run model using the processed data.
        """
        input_encoding, input_ids = input_data
        with torch.no_grad():
            output = self.model(**input_encoding)

            answer_start_probs = torch.nn.functional.softmax(output.start_logits)
            answer_end_probs = torch.nn.functional.softmax(output.end_logits)

            best_answer_start_prob, best_answer_start = torch.max(
                answer_start_probs, dim=1
            )
            best_answer_end_prob, best_answer_end = torch.max(answer_end_probs, dim=1)

            conf = float(best_answer_start_prob * best_answer_end_prob)
            answer = self.tokenizer.convert_tokens_to_string(
                self.tokenizer.convert_ids_to_tokens(
                    input_ids[best_answer_start : best_answer_end + 1]
                )
            )

        return (answer, conf)

    def postprocess(self, inference_output, data):
        """
        Post process inference output into a response.
        """
        answer, conf = inference_output
        response = dict()
        example = self._read_data(data)
        response["id"] = example["uid"]
        response["answer"] = answer if answer != "[CLS]" else ""
        response["conf"] = conf
        self.taskIO.sign_response(response, example)
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
