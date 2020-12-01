# Copyright (c) Facebook, Inc. and its affiliates.
import os

from dynalab_cli import BaseCommand
from dynalab_cli.utils import SetupConfig

MAX_SIZE = 2 * 1024 * 1024 * 1024 # 2GB

class TestLocalCommand(BaseCommand):
    @staticmethod
    def add_args(parser):
        testlocal_parser = parser.add_parser("test-local", help="Check files and test code in local environment")
        testlocal_parser.add_argument("name", type=str, help="Name of the model")


    def __init__(self, args):
        self.args = args

    def run_command(self):
        # Validate config file: all keys exist, required values specified,
        # all specified files exist, handler files in the same directory as handler, 
        # and handler file inherits from the correct base handler

        setup_config = SetupConfig.load_config(self.args.name)
        SetupConfig.validate_config(setup_config)
        print("Config file validated.")

        # Check file size and ask to exclude large files 
        # TODO: do not count size of excluded files; can consider tarball first and count total
        total_size = 0
        for dentry in os.scandir('.'):
            total_size += dentry.stat().st_size
        if setup_config["exclude"]:
            for f in setup_config["exclude"]:
                total_size -= os.path.getsize(f)
        if total_size > MAX_SIZE:
            raise Warning("Size of current repo is more than 2GB. Please consider add to exclude")


        # Run handler locally with task mock context
        # subprocess.run(["python", "-c" ])
        
        # setup_config["handler"]
        # handler.handle()

        import pdb; pdb.set_trace()


