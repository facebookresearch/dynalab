# Copyright (c) Facebook, Inc. and its affiliates.

import subprocess

import requests

from dynalab.config import DYNABENCH_API
from dynalab_cli import BaseCommand
from dynalab_cli.utils import AccessToken, SetupConfigHandler, get_task_id


class UploadCommand(BaseCommand):
    @staticmethod
    def add_args(parser):
        upload_parser = parser.add_parser(
            "upload", help="User Upload and authentication"
        )
        upload_parser.add_argument(
            "-n", "--name", type=str, required=True, help="Name of the model"
        )

    def __init__(self, args):
        self.args = args
        self.config_handler = SetupConfigHandler(args.name)

    def run_command(self):
        # authentication
        # tarball the current directory
        print("Tarballing the project directory...")
        config = self.config_handler.load_config()
        tarball = f"{self.args.name}.tar.gz"
        exclude_command = ""
        if config["exclude"]:
            for f in config["exclude"].split(","):
                exclude_command += f"--exclude={f} "
        exclude_command += f"--exclude=.dynalab/{self.args.name}/tmp"
        process = subprocess.run(
            ["tar", exclude_command, "-czf", tarball, "."],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        if process.returncode != 0:
            raise RuntimeError(
                f"Error in tarballing the current directory {process.stderr}"
            )
        # upload to s3
        print("Uploading file to S3...")
        url = f"{DYNABENCH_API}/models/upload/s3"
        task_id = get_task_id(config["task"])
        with open(tarball, "rb") as f:
            files = {"tarball": f}
            data = {"name": self.args.name, "taskId": task_id}
            r = requests.post(
                url, files=files, data=data, headers=AccessToken().get_headers()
            )
            r.raise_for_status()
            # TODO: show which email address it is: API to fetch email address?
            print(
                f"Your model {self.args.name} has been uploaded to S3 and "
                f"will be deployed shortly. "
                f"You will get an email notification when your model is available "
                f"on Dynabench."
            )
