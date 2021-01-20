# Copyright (c) Facebook, Inc. and its affiliates.

import json
import os
import re
import webbrowser

import requests

from dynalab.config import DYNABENCH_API, DYNABENCH_WEB


class APIToken:
    def __init__(self):
        self.cred_path = os.path.expanduser(
            os.path.join("~", ".dynalab", "secrets.json")
        )

    def save(self, token):
        dirname = os.path.dirname(self.cred_path)
        os.makedirs(dirname, exist_ok=True)
        data = {}
        if os.path.exists(self.cred_path):
            with open(self.cred_path) as f:
                data = json.load(f)

        data["api_token"] = token

        with open(self.cred_path, "w+") as f:
            json.dump(data, f)

    def load(self):
        if os.path.exists(self.cred_path):
            with open(self.cred_path) as f:
                token = json.load(f)["api_token"]
            return token
        raise RuntimeError("You need to first login by dynalab-cli login")

    def delete(self):
        if os.path.exists(self.cred_path):
            data = {}
            with open(self.cred_path) as f:
                data = json.load(f)

            data.pop("api_token", None)
            if len(data) == 0:
                os.remove(self.cred_path)
            else:
                # Some other config is still there, dump it back
                with open(self.cred_path, "w") as f:
                    json.dump(data, f)

    def exists(self):
        if os.path.exists(self.cred_path):
            data = {}
            with open(self.cred_path) as f:
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
        webbrowser.open_new_tab(f"{DYNABENCH_WEB}/generate_api_token")
        user_token = input("Paste your API token here: ")
        api_token.save(user_token)
        print("Successfully logged in.")


def logout():
    api_token = APIToken()
    api_token.delete()
    print("Current account logged out.")


def get_tasks():
    r = requests.get(f"{DYNABENCH_API}/tasks")
    r.raise_for_status()
    tasks = ["_".join(task["shortname"].lower().split()) for task in r.json()]
    return tasks


def get_task_id(shortname):
    r = requests.get(f"{DYNABENCH_API}/tasks")
    r.raise_for_status()
    tasks = r.json()
    for task in tasks:
        if shortname == "_".join(task["shortname"].lower().split()):
            return task["id"]
    raise RuntimeError(
        f"Could not find task {shortname}. Task name must be one of {get_tasks()}"
    )


# some file path utils
def check_path(path, root_dir=".", is_file=True, allow_empty=True):
    if not path:
        return False
    if not os.path.exists(path):
        return False
    if is_file and not os.path.isfile(path):
        return False
    if not allow_empty and os.path.getsize(path) == 0:
        return False
    return os.path.realpath(path).startswith(os.path.realpath(root_dir))


def get_path_inside_rootdir(path, root_dir="."):
    realpath = os.path.realpath(os.path.expanduser(path))
    return realpath[len(os.path.realpath(root_dir)) :].lstrip("/")


def default_filename(key):
    if key in ("handler", "setup"):
        return key + ".py"
    if key == "checkpoint":
        return key + ".pt"
    if key == "requirements":
        return key + ".txt"
    raise NotImplementedError


def check_model_name(name):
    pat = re.compile("^[a-zA-Z0-9-]+$")
    if not pat.match(name):
        raise ValueError(
            "Model name can only contain letters, numbers and "
            "dash (it must satisfy the pattern ^[a-zA-Z0-9-]+$)."
        )


class SetupConfigHandler:
    def __init__(self, name, root_dir="."):
        check_model_name(name)
        self.name = name
        self.config_path = os.path.join(
            root_dir, os.path.join(".dynalab", self.name, "setup_config.json")
        )
        self.config_dir = os.path.dirname(self.config_path)
        self.config_fields = {
            "task",
            "checkpoint",
            "handler",
            "requirements",
            "setup",
            "model_files",
            "exclude",
        }

    def config_exists(self):
        return os.path.exists(self.config_path)

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                return json.load(f)
        else:
            raise RuntimeError(
                f"No config found. Please call dynalab-cli init to initiate this repo. "
            )

    def write_config(self, config):
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_path, "w+") as f:
            f.write(json.dumps(config, indent=4))

    def validate_config(self):
        config = self.load_config()
        contained_fields = set()
        key = "exclude"
        assert key in config, f"Missing config field {key}"
        excluded_files = set()
        if config[key]:
            files = config[key].strip(", ").split(",")
            for f in files:
                assert check_path(
                    f, is_file=False, allow_empty=False
                ), f"{f} is empty or not a valid path"
                excluded_files.add(get_path_inside_rootdir(f))
            config[key] = ",".join(excluded_files)
        for key in config.keys():
            assert key in self.config_fields, f"Invalid config field {key}"
            assert key not in contained_fields, f"Repeated config field {key}"
            contained_fields.add(key)
            if key == "task":
                assert config[key] in get_tasks(), f"Invalid task name {config[key]}"
            elif key in ("checkpoint", "handler"):
                assert check_path(
                    config[key], allow_empty=False
                ), f"{config[key]} is empty or not a valid path"
                f = get_path_inside_rootdir(config[key])
                assert f not in excluded_files, f"{key} file {f} cannot be excluded"
                if key == "handler":
                    assert f.endswith(".py"), f"Handler must be a Python file"
                config[key] = f
            elif key == "model_files":
                if config[key]:
                    files = config[key].strip(", ").split(",")
                    formated_files = set()
                    for f in files:
                        assert check_path(
                            f, allow_empty=False
                        ), f"{f} is empty or not a valid path"
                        assert (
                            f not in excluded_files
                        ), f"{key} file {f} cannot be excluded"
                        formated_files.add(f)
                    config[key] = ",".join(formated_files)
            elif key in ("requirements", "setup"):
                assert isinstance(
                    config[key], bool
                ), f"{key.capitalize()} field must be a boolean true/false"
                if config[key]:
                    assert check_path(default_filename(key), allow_empty=False), (
                        f"Cannot install {key} without or with empty "
                        "./{default_filename(key)}"
                    )

        for field in self.config_fields:
            assert field in contained_fields, f"Missing config field {key}"

        self.write_config(config)
