#!/usr/bin/env python

# Copyright (c) Facebook, Inc. and its affiliates.

# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

from setuptools import find_packages, setup


setup(
    name="dynalab",
    version="0.1",
    packages=find_packages(include=["dynalab"]),
    entry_points={"console_scripts": ["dynalab = dynalab.main:main"]},
    author="Amanpreet Singh",
    author_email="asg@fb.com",
    url="http://dynabench.org",
    include_package_data=True,
    install_requires=["requests>=2.24.0"],
)
