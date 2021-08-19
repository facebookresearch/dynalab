# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import json
import subprocess

from dynalab_cli import BaseCommand
from dynalab_cli.utils import (
    SetupConfigHandler,
    check_model_name,
    check_path,
    default_filename,
    get_path_inside_rootdir,
    get_tasks,
)


class InitCommand(BaseCommand):
    @staticmethod
    def add_args(parser):
        init_parser = parser.add_parser(
            "init", help="Create a starter folder for model upload"
        )

        def model_name_type(name):
            check_model_name(name)
            return str(name)

        init_parser.add_argument(
            "-n",
            "--name",
            type=model_name_type,
            required=True,
            help=(
                "Name of the model, used as a unique identifier, "
                "must be of the pattern ^[a-zA-Z0-9-]+$"
            ),
        )
        tasks, task_codes = get_tasks()
        init_parser.add_argument(
            "-t", "--task", type=str, choices=task_codes, required=True, help="Name of the task"
        )
        init_parser.add_argument(
            "-d",
            "--root-dir",
            type=str,
            default=".",
            help="Root directory to your project folder",
        )
        init_parser.add_argument(
            "--model-checkpoint",
            type=str,
            default=f"./{default_filename('checkpoint')}",
            help="Path to the model checkpoint file",
        )
        init_parser.add_argument(
            "--handler",
            type=str,
            default=f"./{default_filename('handler')}",
            help="Path to the handler file",
        )
        init_parser.add_argument(
            "-r",
            "--install-requirements",
            action="store_true",
            help=(
                "If a requirements.txt file exists, and this flag is true, "
                "we will run pip install -r requirements.txt in the docker"
            ),
        )
        init_parser.add_argument(
            "--run-setup",
            action="store_true",
            help=(
                "If a setup.py file exists and this flag is "
                "true, we will run pip install -e . in the docker"
            ),
        )
        init_parser.add_argument(
            "--model-files",
            type=str,
            default="",
            help=(
                "Comma separated list of files that defines the model, "
                "e.g. vocabulary, config. Once added here, you can directly "
                "import or read these files by name in your handler file "
                "without specifying paths. "
            ),
        )
        init_parser.add_argument(
            "--exclude",
            type=str,
            default="",
            help=(
                "Comma separated list of files or folders to be excluded, e.g. "
                "unnecessary large folders or files like checkpoints"
            ),
        )

        init_parser.add_argument(
            "--amend", action="store_true", help="Update the config"
        )

        init_parser.add_argument(
            "--rename",
            type=model_name_type,
            help="Rename an existing model to a new name",
        )

    def __init__(self, args):
        self.args = args

        # sort out the work_dir path
        self.work_dir = args.root_dir
        self.root_dir = os.path.realpath(os.path.expanduser(args.root_dir))  # full path
        while not os.path.exists(self.root_dir):
            self.work_dir = input(
                f"Please input a valid root path to your repo: "
            )  # user typed path
            self.root_dir = os.path.realpath(os.path.expanduser(self.work_dir))

        self.config_handler = SetupConfigHandler(args.name)
        self.config = {}

    def run_command(self):
        if self.args.rename:
            if not self.config_handler.config_exists():
                raise RuntimeError(
                    f"Model {self.args.name} not found. "
                    f"Unable to rename a non-existing model. "
                )
            else:
                check_model_name(self.args.rename)
                if os.path.exists(
                    os.path.join(
                        self.work_dir, self.config_handler.dynalab_dir, self.args.rename
                    )
                ):
                    raise RuntimeError(
                        f"Model {self.args.rename} already exists. "
                        f"Unable to rename {self.args.name} to {self.args.rename}"
                    )
                else:
                    os.rename(
                        os.path.join(
                            self.work_dir,
                            self.config_handler.dynalab_dir,
                            self.args.name,
                        ),
                        os.path.join(
                            self.work_dir,
                            self.config_handler.dynalab_dir,
                            self.args.rename,
                        ),
                    )
                    print(f"Renamed model {self.args.name} to {self.args.rename}")
            return

        if self.args.amend:
            if not self.config_handler.config_exists():
                raise RuntimeError("Please run dynalab-cli init first")
            EDITOR = os.environ.get("EDITOR", "vim")
            subprocess.run([EDITOR, self.config_handler.config_path])
            try:
                print("Validating the updated config...")
                self.config_handler.validate_config()
            except AssertionError as e:
                raise RuntimeError(
                    f"Validation failed: {e}. "
                    "Please update this field with dynalab-cli init --amend"
                )
            return

        if self.config_handler.config_exists():
            ops = input(
                f"Folder {self.work_dir} already initialized for "
                f"model '{self.args.name}'. Overwrite? [Y/n] "
            )
            if ops.lower() not in ("y", "yes"):
                print(f"Aborting flow. Nothing was done.")
                exit(1)
        print(f"Initializing {self.work_dir} for dynalab model '{self.args.name}'...")

        self.initialize_field("task", self.args.task)
        self.initialize_field("checkpoint", self.args.model_checkpoint)
        self.initialize_field("handler", self.args.handler)
        self.initialize_field("requirements", self.args.install_requirements)
        self.initialize_field("setup", self.args.run_setup)
        self.initialize_field("model_files", self.args.model_files)
        self.initialize_field("exclude", self.args.exclude)

        self.config_handler.write_config(self.config)

        print("Done")

    def update_field(self, key, value):
        self.config[key] = value

    def initialize_field(self, key, value):
        # FIXME: change hard coded tuples to const lists
        if key == "task":
            self.initialize_task(key, value)
        elif key in {"checkpoint", "handler"}:
            self.initialize_path(key, value)
        elif key in ("requirements", "setup"):
            self.initialize_dependency_setting(key, value)
        elif key in ("model_files", "exclude"):
            self.initialize_paths(key, value)
        else:
            raise NotImplementedError(f"{key} not supported in setup_config")

    def initialize_task(self, key, value):
        tasks, task_codes = get_tasks()
        while value not in task_codes:
            message = (
                f"Please choose a valid task name from one of "
                f"[{', '.join(task_codes)}]: "
            )
            value = input(message)

        task_io = [task for task in tasks if task["task_code"] == value][0]["io_def"]
        task_io = json.loads(task_io)

        task_info = {"io_def": task_io, "task": value}

        task_info_path = os.path.join(self.config_handler.root_dir, self.config_handler.dynalab_dir, "task_info.json")
        task_io_dir = os.path.dirname(task_info_path)
        os.makedirs(task_io_dir, exist_ok=True)
        with open(task_info_path, "w+") as f:
            f.write(json.dumps(task_info, indent=4))

        self.update_field(key, value)

    def initialize_path(self, key, value):
        if check_path(value, root_dir=self.root_dir):
            value = get_path_inside_rootdir(value, root_dir=self.root_dir)
            message = (
                f"{key.capitalize()} file found at "
                f"{os.path.join(self.work_dir, value)}. Press enter, or specify "
                f"alternative path [{os.path.join(self.work_dir, value)}]: "
            )
            ops = input(message)
            if ops.lower().strip():
                value = ops

        while not check_path(value, root_dir=self.root_dir):
            message = (
                f"{key.capitalize()} file {value} not a valid path. Please re-specify "
                f"path to {key} file inside the root dir"
            )
            if key == "handler":
                message += (
                    f" or press enter to create a template {key} file at "
                    f"{os.path.join(self.work_dir, default_filename(key))}"
                )
            value = input(f"{message}: ")
            if key == "handler" and not value.strip():
                value = self.create_file(key)
        value = get_path_inside_rootdir(value, root_dir=self.root_dir)

        self.update_field(key, value)

    def initialize_dependency_setting(self, key, value):
        filename = default_filename(key)
        if key == "requirements":
            install_message = "pip install -r requirements.txt"
        elif key == "setup":
            install_message = "pip install -e ."
        if not value and check_path(
            f"{os.path.join(self.root_dir, filename)}", root_dir=self.root_dir
        ):
            ops = input(
                f"{key.capitalize()} file found. Do you want us to install "
                f"dependencies using {os.path.join(self.work_dir, filename)}? [Y/n] "
            )
            if ops.lower().strip() in ("y", "yes"):
                value = True
        elif value and not check_path(
            f"{os.path.join(self.root_dir, filename)}", root_dir=self.root_dir
        ):
            print(
                f"{key.capitalize()} file not found. "
                f"We are unable to install dependencies with {install_message}"
            )
            value = False
        self.update_field(key, value)

    def missing_file(self, key, files):
        is_file = key != "exclude"
        for f in files:
            if not check_path(f, root_dir=self.root_dir, is_file=is_file):
                return f
        return None

    def initialize_paths(self, key, value):
        if not value:
            print(
                f"No {key} path specified. You can "
                f"provide paths by using dynalab-cli init --amend"
            )
            value = []
        else:
            missing = self.missing_file(key, value.strip(", ").split(","))
            while missing:
                if key == "model_files":
                    key_name = "model files"
                elif key == "exclude":
                    key_name = "exclude files or folders"
                value = input(
                    f"Some {key_name} do not have a valid path: {missing}. "
                    f"Please re-enter {key_name} separated by comma or "
                    f"press enter for an empty list: "
                )
                missing = self.missing_file(key, value.strip(", ").split(","))
        if value:
            files = [
                get_path_inside_rootdir(f, root_dir=self.root_dir)
                for f in value.strip(", ").split(",")
            ]
            value = [f for f in files if f]
        self.update_field(key, value)

    def create_file(self, key):
        filename = default_filename(key)
        filepath = os.path.join(self.root_dir, filename)
        printpath = os.path.join(self.work_dir, filename)

        if os.path.exists(filepath):
            ops = input(f"{printpath} exists. Overwrite? [Y/n] ")
            if ops.strip().lower() not in ("y", "yes"):
                return None
        if key == "handler":
            template = os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                "dynalab",
                "handler",
                "handler.py.template",
            )
            with open(template) as f:
                handler_content = f.read()
            with open(filepath, "w") as f:
                f.write(handler_content)
        else:
            open(filepath, "w+").close()
        print(f"Created new {key} file at {printpath}")
        return printpath
