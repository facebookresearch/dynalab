# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import requests

from dynalab.config import DYNABENCH_API
from dynalab_cli import BaseCommand
from dynalab_cli.utils import AccessToken, SetupConfigHandler, get_task_submission_limit
from requests_toolbelt.multipart import encoder
from tqdm import tqdm


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
        # validate config
        try:
            self.config_handler.validate_config()
        except AssertionError as err:
            print(
                f"Error: {err}.\nPlease fix your config file by",
                "dynalab-cli init --amend",
            )
            exit(1)
        else:
            config = self.config_handler.load_config()
            print("Config file validated")

        # set up exclude files for tarball
        print("Tarballing the project directory...")
        tmp_dir = self.config_handler.dynalab_dir / self.args.name / "tmp"
        tmp_dir.mkdir(exist_ok=True)
        exclude_list_file = tmp_dir / "exclude.txt"
        self.config_handler.write_exclude_filelist(
            exclude_list_file, self.args.name, exclude_model=False
        )

        # tarball
        tmp_tarball_dir = tempfile.TemporaryDirectory()
        tarball = Path(tmp_tarball_dir.name) / f"{self.args.name}.tar.gz"
        process = subprocess.run(
            ["tar", f"--exclude-from={exclude_list_file}", "-czf", str(tarball), "."],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        if process.returncode != 0:
            raise RuntimeError(
                f"Error in tarballing the current directory {process.stderr}"
            )
        # upload to s3
        print(
            "Uploading files to S3. For large submissions, the progress bar may "
            "hang a while even after uploading reaches 100%. Please do not kill it..."
        )
        url = f"{DYNABENCH_API}/models/upload/s3"

        payload = encoder.MultipartEncoder(
            {
                "name": self.args.name,
                "taskCode": config["task"],
                "tarball": (
                    f"{self.args.name}.tar.gz",
                    tarball.open("rb"),
                    "application/octet-stream",
                ),
            }
        )
        with tqdm(
            desc="Uploading",
            total=payload.len,
            dynamic_ncols=True,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            payload_monitor = encoder.MultipartEncoderMonitor(
                payload, lambda monitor: pbar.update(monitor.bytes_read - pbar.n)
            )
            headers = {
                **AccessToken().get_headers(),
                "Content-Type": payload.content_type,
            }
            r = requests.post(url, data=payload_monitor, headers=headers)

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            if r.status_code == 429:
                hr_diff, threshold = get_task_submission_limit(config["task"])
                print(
                    f"Failed to submit model {self.args.name} "
                    f"due to submission limit exceeded. No more than {threshold} "
                    f"submissions allowed every {hr_diff} hours for "
                    f"task {config['task']}."
                )
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
        finally:
            os.makedirs(self.config_handler.submission_dir, exist_ok=True)
            submission = (
                self.config_handler.submission_dir
                / datetime.now().strftime("%b-%d-%Y-%H-%M-%S-")
                + tarball.name
            )
            shutil.move(tarball, submission)
            tmp_tarball_dir.cleanup()
            print(
                f"You can inspect the prepared model submission locally at {submission}"
            )
