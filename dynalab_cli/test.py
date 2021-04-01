# Copyright (c) Facebook, Inc. and its affiliates.
import importlib
import os
import shutil
import subprocess
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
            for f in config["exclude"]:
                total_size -= os.path.getsize(f)
        if total_size > MAX_SIZE:
            print(
                "Warning: Size of current project folder is more than 2GB. "
                "Please consider add large files or folders to exclude"
            )

        if self.args.local:
            self.run_local_test(config)

        else:
            tmp_dir = os.path.join(self.config_handler.config_dir, "tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            # tarball everything
            print("Tarballing the project directory...")
            exclude_list_file = os.path.join(tmp_dir, "exclude.txt")
            self.config_handler.write_exclude_filelist(
                exclude_list_file, self.args.name, exclude_model=True
            )
            process = subprocess.run(
                [
                    "tar",
                    f"--exclude-from={exclude_list_file}",
                    "-czf",
                    os.path.join(tmp_dir, f"{self.args.name}.tar.gz"),
                    ".",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            if process.returncode != 0:
                raise RuntimeError(
                    f"Exception in tarballing the project directory {process.stderr}"
                )

            # torch model archive
            print("Archive the model for torchserve...")
            archive_command = [
                "torch-model-archiver",
                "--model-name",
                self.args.name,
                "--serialized-file",
                config["checkpoint"],
                "--handler",
                config["handler"],
                "--version",
                "1.0",
                "-f",
                "--export-path",
                tmp_dir,
            ]
            if config["model_files"]:
                archive_command += ["--extra-files", ",".join(config["model_files"])]
            process = subprocess.run(
                archive_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            if process.returncode != 0:
                raise RuntimeError(f"Exception in torchserve archive {process.stderr}")

            # pull docker
            lib_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                "dynalab",
                "dockerfiles",
            )
            docker_path = os.path.join(tmp_dir, "Dockerfile")
            # TODO: pull the files from dynalab repo once public
            shutil.copyfile(os.path.join(lib_dir, "Dockerfile.dev"), docker_path)
            shutil.copyfile(
                os.path.join(lib_dir, "dev-docker-entrypoint.sh"),
                os.path.join(tmp_dir, "dev-docker-entrypoint.sh"),
            )

            # build docker
            print("Building docker image...")
            docker_build_args = [
                "--build-arg",
                f"add_dir={tmp_dir}",
                "--build-arg",
                f"model_name={self.args.name}",
                "--build-arg",
                f"requirements={str(config['requirements'])}",
                "--build-arg",
                f"setup={str(config['setup'])}",
            ]
            docker_build_command = [
                "docker",
                "build",
                "--network",
                "host",
                "-t",
                self.args.name,
                "-f",
                docker_path,
                ".",
            ] + docker_build_args

            subprocess.run(docker_build_command)
            process = subprocess.run(
                f"docker run {self.args.name}",
                shell=True,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            ts_log = os.path.join(tmp_dir, "ts_log.log")
            with open(ts_log, "w") as f:
                f.write(process.stderr)
            if process.returncode != 0:
                raise RuntimeError(
                    f"Integrated test failed. Please refer to "
                    f"{ts_log} for detailed torchserve log."
                )
            else:
                print(
                    f"Integrated test passed. "
                    f"Torchserve log can be found at {ts_log}"
                )

            # clean up local tarball, .mar and intermediate docker layers
            os.remove(os.path.join(tmp_dir, f"{self.args.name}.tar.gz"))
            os.remove(os.path.join(tmp_dir, f"{self.args.name}.mar"))
            print(
                "We suggest removing unused docker data by `docker system prune`, "
                "including unused containers, networks and images. "
                "To do so, choose 'y' for the following prompt. "
                "More info available at "
                "https://docs.docker.com/engine/reference/commandline/system_prune/"
            )
            subprocess.run(f"docker system prune", shell=True)

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
        taskIO.show_mock_input_data()

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
