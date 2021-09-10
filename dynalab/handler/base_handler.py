# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os

import torch
from ts.torch_handler.base_handler import BaseHandler


class BaseDynaHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.initialized = False

    def _handler_initialize(self, context):
        """
        Helper function to initialize the variables neccessary for the handler
        """
        manifest = context.manifest
        properties = context.system_properties
        model_pt_path = os.path.join(
            properties["model_dir"], manifest["model"]["serializedFile"]
        )
        model_file_dir = properties["model_dir"]
        device_str = (
            "cuda:" + str(properties["gpu_id"])
            if properties["gpu_id"] is not None and torch.cuda.is_available()
            else "cpu"
        )

        return model_pt_path, model_file_dir, device_str

    def _read_data(self, data):
        return data[0]["body"]
