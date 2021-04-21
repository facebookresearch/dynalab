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
data=$(python -c "from dynalab.tasks.${task} import TaskIO; taskIO = TaskIO(); print(taskIO.get_input_json())")
echo Input test data is $data
response=$(curl http://127.0.0.1:8080/predictions/$model_name --header "Content-Type: application/json" --data "$data" --request POST --fail)
retries=0
while [[ -z $response ]] && [[ $retries -le 3 ]]; do
    echo "Model $model_name failed to respond. Retry in 30s [$retries / 3]"
    retries=$(($retries+1))
    sleep 30
    response=$(curl http://127.0.0.1:8080/predictions/$model_name --header "Content-Type: application/json" --data "$data" --request POST --fail)
done

if [[ -z $response ]]; then
    ex=$(curl http://127.0.0.1:8080/predictions/$model_name --header "Content-Type: application/json" --data "$data" --request POST)
    echo "The exception message from $model_name is $ex"
    exit 1
else
    echo "Your model $model_name response is $response"
    python -c "from dynalab.tasks.${task} import TaskIO; taskIO = TaskIO($data); taskIO.verify_response($response)" || exit 1
fi

exit 0
