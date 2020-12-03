# Copyright (c) Facebook, Inc. and its affiliates.
import os
import subprocess

from dynalab_cli import BaseCommand
from dynalab_cli.utils import SetupConfigHandler


MAX_SIZE = 2 * 1024 * 1024 * 1024  # 2GB


class TestLocalCommand(BaseCommand):
    @staticmethod
    def add_args(parser):
        testlocal_parser = parser.add_parser(
            "test-local", help="Check files and test code in local environment"
        )
        testlocal_parser.add_argument(
            "-n", "--name", type=str, help="Name of the model"
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
        # with open(os.path.join(self.config_handler.config_dir, 'tmp', 'test_handler.py')) as f:
        #     print(f.read())
        
        subprocess.run(["python", f"{os.path.join(self.config_handler.config_dir, 'tmp', 'test_handler.py')}", f"{config['handler']}"])

        # TODO
        # Run handler locally with task mock context
        # subprocess.run(["python", "-c" ])

        # setup_config["handler"]
        # handler.handle()