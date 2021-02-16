#!/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

set -e

if [[ "$1" = "serve" ]]; then
    shift 1
    printenv
    ls /opt
    torchserve --start --ts-config /home/model-server/config.properties
else
    eval "$@"
fi

# prevent docker exit
tail -f /dev/null
