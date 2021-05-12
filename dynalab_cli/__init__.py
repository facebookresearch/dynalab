# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod
from argparse import ArgumentParser


class BaseCommand(ABC):
    @staticmethod
    @abstractmethod
    def add_args(parser: ArgumentParser):
        raise NotImplementedError()

    def __init__(self, args):
        pass

    @abstractmethod
    def run_command(self):
        raise NotImplementedError()
