# Copyright (c) Facebook, Inc. and its affiliates.

import os
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
        tmp_dir = os.path.join(".dynalab", self.args.name, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        with open(os.path.join(tmp_dir, "exclude.txt"), "w+") as f:
            if config["exclude"]:
                for ex in config["exclude"].split(","):
                    f.write(ex + "\n")
            for m in os.listdir(".dynalab"):
                if m != self.args.name:
                    f.write(os.path.join(".dynalab", m) + "\n")
            f.write(tmp_dir)
        process = subprocess.run(
            [
                "tar",
                f"--exclude-from={os.path.join(tmp_dir, 'exclude.txt')}",
                "-czf",
                tarball,
                ".",
            ],
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
