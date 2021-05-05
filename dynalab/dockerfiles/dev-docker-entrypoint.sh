#!/bin/bash

# Copyright (c) Facebook, Inc. and its affiliates.

model_name=$1
# read task from config to make sure that config file is not excluded in the tarball
config_path="/home/model-server/code/.dynalab/${model_name}/setup_config.json"
task=$(python -c "import json; config=json.load(open('$config_path')); print(config['task'])")

echo "Running integrated test for model $model_name on task $task"

set -m

# start torchserve
torchserve --start --ncs --models ${model_name}.mar --model-store /opt/ml/model 1>&2 &

status=unknown
while [[ $status != Healthy ]]; do
    if [[ $status = Unhealthy ]] || [[ $status == "Partial Healthy" ]]; then
        echo "Serving model failed."
        exit 1
    fi
    sleep 30
    status=$(curl -s http://localhost:8080/ping | python -c "import json, sys; obj=json.load(sys.stdin);print(obj['status'])") || exit 1
done
echo "Health ping passed. Start model inference..."

# test the model endpoint, consider moving all these into a python script in the future?
endpoint_url="http://127.0.0.1:8080/predictions/$model_name"
python -c "import sys; from dynalab.tasks.${task} import TaskIO, data; TaskIO().test_endpoint_individually(sys.argv[1], data)" $endpoint_url
