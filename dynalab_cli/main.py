# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from argparse import ArgumentParser

from dynalab_cli.init import InitCommand
from dynalab_cli.test import TestCommand
from dynalab_cli.upload import UploadCommand
from dynalab_cli.user import LoginCommand, LogoutCommand


command_map = {
    "login": LoginCommand,
    "logout": LogoutCommand,
    "init": InitCommand,
    "test": TestCommand,
    "upload": UploadCommand,
}


def main():
    parser = ArgumentParser(prog="dynalab-cli")
    subparsers = parser.add_subparsers(help="dynalab-cli command help", dest="option")

    LoginCommand.add_args(subparsers)
    LogoutCommand.add_args(subparsers)
    InitCommand.add_args(subparsers)
    TestCommand.add_args(subparsers)
    UploadCommand.add_args(subparsers)

    args = parser.parse_args()

    command_map[args.option](args).run_command()


if __name__ == "__main__":
    main()
