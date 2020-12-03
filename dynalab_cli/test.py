# Copyright (c) Facebook, Inc. and its affiliates.
import os
import subprocess

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

        test_handler = self.compose_test_handler_file(config)
        subprocess.run(["python", test_handler])

        if not self.args.local:
            # pull docker
            pass

    def compose_test_handler_file(self, config):
        test_handler = os.path.join(
            self.config_handler.config_dir, "tmp", "test_handler.py"
        )
        os.makedirs(os.path.join(self.config_handler.config_dir, "tmp"), exist_ok=True)

        handler_dir = os.path.join(".", os.path.dirname(config["handler"]))
        handler_name = os.path.splitext(os.path.basename(config["handler"]))[0]

        import_handler_command = (
            f"import sys\nsys.path.append('{handler_dir}')\n"
            f"handler = __import__('{handler_name}')\n"
        )
        import_context_command = (
            f"from dynalab.tasks.{config['task']} import get_mock_input\n"
        )

        run_command = (
            f"if __name__ == '__main__':\n"
            f"    data, context = get_mock_input('{self.args.name}')\n"
            f"    handler.handle(data=data, context=context)\n"
            f"    print('Local test passed')\n"
        )
        with open(test_handler, "w+") as f:
            f.write(import_handler_command)
            f.write(import_context_command)
            f.write(run_command)
        return test_handler
