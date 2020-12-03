# Copyright (c) Facebook, Inc. and its affiliates.

import json
import os
from getpass import getpass

import requests

from dynalab.config import DYNABENCH_API


class AuthToken:
    def __init__(self):
        self.token_path = os.path.expanduser("~/.dynalab/token")

    def save_token(self, token):
        dirname = os.path.dirname(self.token_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(self.token_path, "w+") as f:
            f.write(token)

    def load_token(self):
        if os.path.exists(self.token_path):
            with open(self.token_path) as f:
                token = f.read().strip()
            return token
        raise FileNotFoundError("You need to first login by dynalab-cli login")

    def delete_token(self):
        if os.path.exists(self.token_path):
            os.remove(self.token_path)

    def exists(self):
        if os.path.exists(self.token_path):
            return True
        return False


def login():
    authToken = AuthToken()
    if authToken.exists():
        ops = input(
            "An account is already logged in. \
            Do you want to logout and re-login another account? (Y/N)\n"
        )
        if ops.lower().strip() == "y":
            logout()
        else:
            print("Current account remains logged in.")
    else:
        email = input("Your DynaBench registered email address: ")
        password = getpass(prompt="Password: ")
        r = requests.post(
            f"{DYNABENCH_API}/authenticate", json={"email": email, "password": password}
        )
        r.raise_for_status()
        authToken.save_token(r.json()["token"])
        print("Successfully logged in.")


def logout():
    authToken = AuthToken()
    authToken.delete_token()
    print("Current account logged out.")


def get_tasks():
    r = requests.get(f"{DYNABENCH_API}/tasks")
    r.raise_for_status()
    tasks = ["_".join(task["shortname"].lower().split()) for task in r.json()]
    return tasks


# some file path utils
def check_path(path, root_dir=".", is_file=True):
    if not path:
        return False
    if not os.path.exists(path):
        return False
    if is_file and not os.path.isfile(path):
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


# TODO: WIP
class SetupConfigHandler:
    def __init__(self, name):
        self.name = name
        self.config_path = f"./.dynalab/{self.name}/setup_config.json"
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
        if config[key]:
            files = config[key].strip(", ").split(",")
            excluded_files = set()
            for f in files:
                assert check_path(f, is_file=False), f"{f} not a valid path"
                excluded_files.add(get_path_inside_rootdir(f))
            config[key] = ",".join(excluded_files)
        for key in config.keys():
            assert key in self.config_fields, f"Invalid config field {key}"
            assert key not in contained_fields, f"Repeated config field {key}"
            contained_fields.add(key)
            if key == "task":
                assert config[key] in get_tasks(), f"Invalid task name {config[key]}"
            elif key in ("checkpoint", "handler"):
                assert check_path(config[key]), f"{config[key]} not a valid path"
                f = get_path_inside_rootdir(config[key])
                assert f not in excluded_files, f"{key} file {f} cannot be excluded"
                config[key] = f
            elif key == "model_files":
                if config[key]:
                    handler_dir = os.path.dirname(os.path.realpath(config["handler"]))
                    files = config[key].strip(", ").split(",")
                    formated_files = set()
                    for f in files:
                        assert check_path(f), f"{f} not a valid path"
                        f = get_path_inside_rootdir(f)
                        assert os.path.dirname(os.path.realpath(f)) == handler_dir, (
                            f"Model files {f} not under the same level "
                            "as handler file {config['handler']}"
                        )
                        assert (
                            f not in excluded_files
                        ), f"{key} file {f} cannot be excluded"
                        formated_files.add(f)
                    config[key] = ",".join(formated_files)
            elif key in ("requirements", "setup"):
                if config[key]:
                    assert check_path(default_filename(key))

        for field in self.config_fields:
            assert field in contained_fields, f"Missing config field {key}"

        self.write_config(config)
