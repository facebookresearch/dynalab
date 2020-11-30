# Copyright (c) Facebook, Inc. and its affiliates.

from dynalab_cli import BaseCommand
<<<<<<< HEAD
from dynalab_cli.utils import login, logout
=======
from dynalab_cli.utils import User
>>>>>>> Dynalab cli framework, init and basic login


class LoginCommand(BaseCommand):
    @staticmethod
    def add_args(parser):
        login_parser = parser.add_parser("login", help="User login and authentication")

    def run_command(self):
<<<<<<< HEAD
        login()
=======
        User.login()
>>>>>>> Dynalab cli framework, init and basic login


class LogoutCommand(BaseCommand):
    @staticmethod
    def add_args(parser):
        logout_parser = parser.add_parser("logout", help="User logout")

    def run_command(self):
<<<<<<< HEAD
        logout()
=======
        User.logout()
>>>>>>> Dynalab cli framework, init and basic login
