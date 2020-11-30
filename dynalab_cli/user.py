# Copyright (c) Facebook, Inc. and its affiliates.

from dynalab_cli import BaseCommand
from dynalab_cli.utils import login, logout


class LoginCommand(BaseCommand):
    @staticmethod
    def add_args(parser):
        login_parser = parser.add_parser("login", help="User login and authentication")

    def run_command(self):
        login()


class LogoutCommand(BaseCommand):
    @staticmethod
    def add_args(parser):
        logout_parser = parser.add_parser("logout", help="User logout")

    def run_command(self):
        logout()
