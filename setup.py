#!/usr/bin/env python

# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from setuptools import find_packages, setup


setup(
    name="dynalab",
    version="0.1",
    packages=find_packages(
        include=["dynalab", "dynalab_cli", "dynalab.handler", "dynalab.tasks"]
    ),
    entry_points={"console_scripts": ["dynalab-cli = dynalab_cli.main:main"]},
    author="Dynabench",
    author_email="dynabench@fb.com",
    url="http://dynabench.org",
    include_package_data=True,
    install_requires=[
        "requests>=2.24.0",
        "torchserve>=0.2.0",
        "torch-model-archiver>=0.2.0",
    ],
)
