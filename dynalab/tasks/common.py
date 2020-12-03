# Copyright (c) Facebook, Inc. and its affiliates.

import os

from ts.context import Context

from dynalab_cli.utils import SetupConfigHandler


def get_mock_context(model_name):
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
