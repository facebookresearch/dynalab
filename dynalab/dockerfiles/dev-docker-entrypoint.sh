#!/bin/bash

# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

model_name=$1
# read task from config to make sure that config file is not excluded in the tarball
config_path="/home/model-server/code/.dynalab/${model_name}/setup_config.json"
task=$(python -c "import json; config=json.load(open('$config_path')); print(config['task'])")

task_info_path="/home/model-server/code/.dynalab/${model_name}/task_info.json"

echo "Running integrated test for model $model_name on task $task..."

set -m

# start torchserve
echo "Start serving model..."
torchserve --start --ncs --models ${model_name}.mar --model-store /opt/ml/model 1>&2 &

# health ping to make sure the http connection is on
echo "Check model loading status..."
status=$(curl -s http://localhost:8080/ping)
while [[ $status != Healthy ]]; do
    if [[ -z $status ]]; then
        echo "HTTP connection has not yet been set up. Sleep 30..."
        sleep 30
        status=$(curl -s http://localhost:8080/ping)
    else
        status=$(python -c "import json; print($status['status'])")
        if [[ $status = Unhealthy ]]; then
            echo "Serving model failed."
            exit 1
        fi
    fi
done
echo "Health ping passed. Start model inference..."

# run inference
endpoint_url="http://127.0.0.1:8080/predictions/$model_name"
python -c "import sys; from dynalab.tasks.task_io import TaskIO; TaskIO(sys.argv[1]).test_endpoint_individually(sys.argv[2])" $task_info_path $endpoint_url
