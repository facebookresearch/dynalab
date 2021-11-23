# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import re
import webbrowser
from pathlib import Path

import requests

from dynalab.config import DYNABENCH_API, DYNABENCH_WEB


class APIToken:
    def __init__(self):
        self.cred_path = (Path("~") / ".dynalab" / "secrets.json").expanduser()

    def save(self, token):
        dirname = self.cred_path.parent
        dirname.mkdir(exist_ok=True)
        data = {}
        if self.cred_path.exists():
            with self.cred_path.open() as f:
                data = json.load(f)

        data["api_token"] = token

        with self.cred_path.open("w+") as f:
            json.dump(data, f)

    def load(self):
        if self.cred_path.exists():
            with self.cred_path.open() as f:
                token = json.load(f)["api_token"]
            return token
        raise RuntimeError("You need to first login by dynalab-cli login")

    def delete(self):
        if self.cred_path.exists():
            data = {}
            with self.cred_path.open() as f:
                data = json.load(f)

            data.pop("api_token", None)
            if len(data) == 0:
                self.cred_path.unlink()
            else:
                # Some other config is still there, dump it back
                with self.cred_path.open("w") as f:
                    json.dump(data, f)

    def exists(self):
        if self.cred_path.exists():
            data = {}
            with self.cred_path.open() as f:
                data = json.load(f)
            return "api_token" in data
        return False


class AccessToken:
    def __init__(self):
        self.api_token = APIToken().load()

    @property
    def headers(self):
        return self.get_headers()

    def fetch(self):
        url = f"{DYNABENCH_API}/authenticate/refresh_from_api"
        payload = {"api_token": self.api_token}
        r = requests.get(url, params=payload)
        r.raise_for_status()
        access_token = r.json()["token"]
        return access_token

    def get_headers(self):
        return {"Authorization": f"Bearer {self.fetch()}"}


def login():
    api_token = APIToken()
    if api_token.exists():
        ops = input(
            "An account is already logged in. \
            Do you want to logout and re-login another account? (Y/N)\n"
        )
        if ops.lower().strip() == "y":
            logout()
        else:
            print("Current account remains logged in.")
    else:
        print(
            "A browser window will open prompting you to login, "
            + "after login please copy the API token and paste it here"
        )
        print(f"Opening in browser: {DYNABENCH_WEB}/generate_api_token")
        webbrowser.open_new_tab(f"{DYNABENCH_WEB}/generate_api_token")
        user_token = input("Paste your API token here: ")
        api_token.save(user_token)
        print("Successfully logged in.")


def logout():
    api_token = APIToken()
    api_token.delete()
    print("Current account logged out.")


def get_tasks():
    r = requests.get(f"{DYNABENCH_API}/tasks/submitable")
    r.raise_for_status()
    tasks = [task for task in r.json() if task["task_code"]]
    task_codes = [task["task_code"] for task in tasks]
    return tasks, task_codes


def get_task_submission_limit(task_code):
    hr_diff = 24
    threshold = 3
    r = requests.get(f"{DYNABENCH_API}/tasks/submitable")
    r.raise_for_status()
    for task in r.json():
        if task["task_code"] == task_code:
            if task["dynalab_hr_diff"] is not None:
                hr_diff = task["dynalab_hr_diff"]
            if task["dynalab_threshold"] is not None:
                threshold = task["dynalab_threshold"]
            return hr_diff, threshold
    return hr_diff, threshold


# some file path utils
def check_path(path, root_dir=".", is_file=True, allow_empty=True):
    path = Path(path)
    if not path:
        return False
    if not path.exists():
        return False
    if is_file and not path.is_file():
        return False
    if not allow_empty and path.stat().st_size == 0:
        return False
    return str(path.resolve()).startswith(str(root_dir.resolve()))


def get_path_inside_rootdir(path, root_dir="."):
    return (
        Path(path)
        .expanduser()
        .resolve()
        .relative_to(Path(root_dir).expanduser().resolve())
    )


def default_filename(key):
    if key in ("handler", "setup"):
        return key + ".py"
    if key == "checkpoint":
        return key + ".pt"
    if key == "requirements":
        return key + ".txt"
    raise NotImplementedError


def check_model_name(name):
    pat = re.compile("^[a-z0-9-]+$")
    if not pat.match(name):
        raise ValueError(
            "Model name can only contain letters, numbers and "
            "dash (it must satisfy the pattern ^[a-z0-9-]+$)."
        )


class SetupConfigHandler:
    def __init__(self, name, root_dir="."):
        """
        The funtions only work right if called from root_dir
        """
        check_model_name(name)
        self.name = name
        self.root_dir = Path(root_dir)
        self.dynalab_dir = Path(".dynalab")
        self.config_path = root_dir / self.dynalab_dir / self.name / "setup_config.json"
        self.config_dir = self.config_path.parent
        self.config_fields = {
            "task",
            "checkpoint",
            "handler",
            "requirements",
            "setup",
            "model_files",
            "exclude",
        }
        self.submission_dir = Path(".dynalab_submissions")

    def config_exists(self):
        return self.config_path.exists()

    def load_config(self):
        if self.config_path.exists():
            with self.config_path.open() as f:
                return json.load(f)
        else:
            raise RuntimeError(
                f"No config found. Please call dynalab-cli init to initiate this repo. "
            )

    def write_config(self, config):
        self.config_dir.mkdir(exist_ok=True)
        config["checkpoint"] = str(config["checkpoint"])
        config["handler"] = str(config["handler"])
        with self.config_path.open("w+") as f:
            f.write(json.dumps(config, indent=4))

    def validate_config(self):
        config = self.load_config()
        contained_fields = set()
        key = "exclude"
        assert key in config, f"Missing config field {key}"
        excluded_files = set()
        if config[key]:
            files = config[key]
            for f in files:
                assert check_path(
                    self.root_dir / f,
                    root_dir=self.root_dir,
                    is_file=False,
                    allow_empty=True,
                ), f"{f} is not a valid path"
                excluded_files.add(f)
            config[key] = ",".join(excluded_files)
        for key in config.keys():
            assert key in self.config_fields, f"Invalid config field {key}"
            assert key not in contained_fields, f"Repeated config field {key}"
            contained_fields.add(key)
            if key == "task":
                _, task_codes = get_tasks()
                assert config[key] in task_codes, f"Invalid task name {config[key]}"
            elif key in ("checkpoint", "handler"):
                assert check_path(
                    self.root_dir / config[key],
                    root_dir=self.root_dir,
                    allow_empty=False,
                ), f"{config[key]} is empty or not a valid path"
                assert (
                    config[key] not in excluded_files
                ), f"{key} file {config[key]} cannot be excluded"
                if key == "handler":
                    assert config[key].endswith(".py"), f"Handler must be a Python file"
            elif key == "model_files":
                if config[key]:
                    files = config[key]
                    for f in files:
                        assert check_path(
                            self.root_dir / f, root_dir=self.root_dir, allow_empty=False
                        ), f"{key} path {f} is empty or not a valid path"
                        assert (
                            f not in excluded_files
                        ), f"{key} file {f} cannot be excluded"
            elif key in ("requirements", "setup"):
                assert isinstance(
                    config[key], bool
                ), f"{key.capitalize()} field must be a boolean true/false"
                if config[key]:
                    assert check_path(
                        self.root_dir / default_filename(key),
                        root_dir=self.root_dir,
                        allow_empty=False,
                    ), (
                        f"Cannot install {key} without or with empty "
                        f"./{default_filename(key)}"
                    )

        for field in self.config_fields:
            assert field in contained_fields, f"Missing config field {key}"

    def write_exclude_filelist(self, outfile, model_name, exclude_model=False):
        def _write_exclude_entry_safe(file, f_obj):
            if (self.root_dir / file).exists():
                f_obj.write(str(file) + "\n")

        config = self.load_config()
        with Path(outfile).open("w") as f:
            # exclude itself
            _write_exclude_entry_safe(outfile, f)

            # all exclude files and folders
            if config["exclude"]:
                for ex in config["exclude"]:
                    _write_exclude_entry_safe(ex, f)

            # tmp dir for test
            tmp_dir = self.config_dir / "tmp"
            _write_exclude_entry_safe(tmp_dir, f)

            # past submissions
            _write_exclude_entry_safe(self.submission_dir, f)

            # dir for other models
            if self.dynalab_dir.exists():
                for m in self.dynalab_dir.iterdir():
                    if m != model_name:
                        _write_exclude_entry_safe(self.dynalab_dir / m, f)

            if exclude_model:
                _write_exclude_entry_safe(config["checkpoint"], f)
                _write_exclude_entry_safe(config["handler"], f)
