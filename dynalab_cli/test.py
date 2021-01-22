# Copyright (c) Facebook, Inc. and its affiliates.
import importlib
import os
import sys

from dynalab_cli import BaseCommand
from dynalab_cli.utils import SetupConfigHandler


MAX_SIZE = 2 * 1024 * 1024 * 1024  # 2GB


class TestCommand(BaseCommand):
    @staticmethod
    def add_args(parser):
        test_parser = parser.add_parser(
            "test", help="Check files and test code in local environment"
        )
        test_parser.add_argument(
            "-n", "--name", type=str, required=True, help="Name of the model"
        )
        test_parser.add_argument(
            "--local", action="store_true", help="whether to run local test only"
        )

    def __init__(self, args):
        self.args = args
        self.config_handler = SetupConfigHandler(args.name)

    def run_command(self):
        # Validate config file: all keys exist, required values specified,
        # all specified files exist, handler files in the same directory as handler,
        # and handler file inherits from the correct base handler
        try:
            self.config_handler.validate_config()
            print("Config file validated.")
        except AssertionError as err:
            print(
                f"Error: {err}.\nPlease fix your config file by",
                "dynalab-cli init --amend",
            )
            exit(1)

        config = self.config_handler.load_config()

        # Check file size and ask to exclude large files
        total_size = 0
        for dentry in os.scandir("."):
            total_size += dentry.stat().st_size
        if config["exclude"]:
            for f in config["exclude"].split(","):
                total_size -= os.path.getsize(f)
        if total_size > MAX_SIZE:
            print(
                "Warning: Size of current project folder is more than 2GB. "
                "Please consider add large files or folders to exclude"
            )

        if self.args.local:
            self.run_local_test(config)

        if not self.args.local:
            # pull docker
            pass

    def run_local_test(self, config):
        # load handler
        sys.path.append(os.getcwd())
        handler_spec = importlib.util.spec_from_file_location(
            "handler", config["handler"]
        )
        handler = importlib.util.module_from_spec(handler_spec)
        handler_spec.loader.exec_module(handler)

        # load taskIO
        taskIO = importlib.import_module(f"dynalab.tasks.{config['task']}").TaskIO()

        print("Obtaining test input data...")
        data, context = taskIO.get_mock_input(self.args.name)
        taskIO.show_mock_input_data(data)

        print("Getting model response...")
        response = taskIO.mock_handle(handler.handle, data, context)
        taskIO.show_model_response(response)

        print("Verifying model response...")
        try:
            taskIO.verify_mock_response(response)
        except Exception as e:
            raise RuntimeError(f"Local test failed because of: {e}")
        else:
            print("Local test passed")
