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
        raise RuntimeError("You need to first login by dynalab-cli login")

    def delete_token(self):
        if os.path.exists(self.token_path):
            os.remove(self.token_path)

    def exists(self):
        if os.path.exists(self.token_path):
            return True
        return False


def login():
    auth_token = AuthToken()
    if auth_token.exists():
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
        auth_token.save_token(r.json()["token"])
        print("Successfully logged in.")


def logout():
    auth_token = AuthToken()
    auth_token.delete_token()
    print("Current account logged out.")


def get_tasks():
    r = requests.get(f"{DYNABENCH_API}/tasks")
    r.raise_for_status()
    tasks = ["_".join(task["shortname"].lower().split()) for task in r.json()]
    return tasks


# TODO: WIP
class SetupConfigHandler:
    def __init__(self, name):
        self.name = name
        self.config_path = f"./.dynalab/{self.name}/setup_config.json"
        self.config_dir = os.path.dirname(self.config_path)

    def config_exists(self):
        return os.path.exists(self.config_path)

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                return json.load(f)
        else:
            raise RuntimeError(f"Please call dynalab-cli init to initiate this repo. ")

    def write_config(self, config):
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_path, "w+") as f:
            f.write(json.dumps(config, indent=4))
