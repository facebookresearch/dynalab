# Copyright (c) Facebook, Inc. and its affiliates.

import json
import os
import sys
from pathlib import Path

import sentencepiece
import torch

import fairseq.checkpoint_utils
from dynalab.handler.base_handler import BaseDynaHandler
from dynalab.tasks.flores_small1 import TaskIO
from fairseq.sequence_generator import SequenceGenerator
from fairseq.tasks.translation import TranslationConfig, TranslationTask


class Handler(BaseDynaHandler):
    def initialize(self, context):
        """
        load model and extra files
        """
        model_pt_path, model_file_dir, device = self._handler_initialize(context)

        translation_cfg = TranslationConfig()
        vocab = TranslationTask.load_dictionary("dict.txt")
        task = TranslationTask(translation_cfg, vocab, vocab)
        self.vocab = vocab
        [model], cfg = fairseq.checkpoint_utils.load_model_ensemble(
            [model_pt_path], task=task
        )

        self.model = model
        self.model.eval().to(device)
        self.sequence_generator = SequenceGenerator(
            [self.model],
            tgt_dict=self.vocab,
            # TODO: read this from a config file
            beam_size=1,
            max_len_a=1.3,
            max_len_b=5,
            min_len=5,
        )

        self.spm = sentencepiece.SentencePieceProcessor()
        self.spm.Load("sentencepiece.bpe.model")
        # #################################################

        self.taskIO = TaskIO()
        self.initialized = True

    def lang_token(self, lang: str) -> int:
        # M2M uses 2 letter language codes.
        simple_lang = lang.split("_")[0]
        token = self.vocab.index(f"__{simple_lang}__")
        assert token != self.vocab.unk(), f"Unknown language '{lang}' ({simple_lang})"
        return token

    def tokenize(self, line: str) -> list:
        words = self.spm.EncodeAsPieces(line.strip())
        tokens = [self.vocab.index(word) for word in words]
        return tokens

    def preprocess(self, data):
        """
        preprocess data into a format that the model can do inference on
        """
        # TODO: this doesn't seem to produce good results. wrong EOS / BOS ?
        sample = self._read_data(data)
        tokens = self.tokenize(sample["source_text"])
        sample["net_input"] = {
            "src_tokens": torch.tensor([tokens + [self.lang_token(sample["source_language"])]]),
            "src_lengths": torch.tensor([len(tokens)]),
        }
        sample["tgt_lang"] = self.lang_token(sample["target_language"])
        return sample

    @torch.no_grad()
    def inference(self, input_data: dict) -> list:
        """
        """
        generated = self.sequence_generator.generate(
            models=[], sample=input_data, bos_token=input_data["tgt_lang"]
        )
        # `generate` returns a list of samples
        # with several hypothesis per sample
        # and a dict per hypothesis
        return generated[0][0]["tokens"]

    def postprocess(self, inference_output, data):
        """
        post process inference output into a response.
        response should be a single element list of a json
        the response format will need to pass the validation in
        ```
        dynalab.tasks.flores-small1.TaskIO().verify_response(response)
        ```
        """
        example = self._read_data(data)
        translation = self.vocab.string(inference_output, "sentencepiece")
        response = {
            "id": example["uid"],
            "source_language": example["source_language"],
            "source_text": example["source_text"],
            "target_language": example["target_language"],
            "translated_text": translation,
        }

        # #################################################
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
