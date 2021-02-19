# Copyright (c) Facebook, Inc. and its affiliates.

import os

import torch
from ts.torch_handler.base_handler import BaseHandler


class BaseDynaHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.initialized = False

    def _handler_initialize(self, context):
        """
        Helper function to initializes the variables neccessary for the handler
        """
        manifest = context.manifest
        properties = context.system_properties
        model_pt_path = os.path.join(
            properties["model_dir"], manifest["model"]["serializedFile"]
        )
        extra_file_dir = properties["model_dir"]
        device = torch.device(
            "cuda:" + str(properties["gpu_id"]) if torch.cuda.is_available() else "cpu"
        )

        return model_pt_path, extra_file_dir, device

    def _read_data(self, data):
        return data[0]["body"]
