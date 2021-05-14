# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

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
        exclude_list_file = os.path.join(tmp_dir, "exclude.txt")
        self.config_handler.write_exclude_filelist(
            exclude_list_file, self.args.name, exclude_model=False
        )
        process = subprocess.run(
            ["tar", f"--exclude-from={exclude_list_file}", "-czf", tarball, "."],
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
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as ex:
                if r.status_code == 429:
                    print(f"Failed to submit model {self.args.name} due to submission limit exceeded")
                else:
                    print(f"Failed to submit model due to: {ex}")
            except Exception as ex:
                print(f"Failed to submit model due to: {ex}")
            # TODO: show which email address it is: API to fetch email address?
            else:
                print(
                    f"Your model {self.args.name} has been uploaded to S3 and "
                    f"will be deployed shortly. "
                    f"You will get an email notification when your model is available "
                    f"on Dynabench."
                )
