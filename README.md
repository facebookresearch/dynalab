## What is Dynalab?
Imagine you developed a fancy model, living in `/path/to/fancy_project`, and you want to share your amazing results on the [Dynabench](www.dynabench.org) model leaderboard. Dynalab makes it easy for you to do just that.
## Installation

```
pip install dynalab
```

You will also need to install [docker](https://www.docker.com/products/docker-desktop).

## Model submission workflow

### Step 1: Initialize the project folder
Run the following command to initialize your project folder for model upload:
```
$ cd /path/to/fancy_project # We will refer to this as the root path
$ dynalab-cli init -n <name_of_your_model>
```
Follow the prompts to configure this folder. You can find more information about the config of files by running `dynalab-cli init -h`. **Make sure that all files you specified on initialization are physically inside this project folder, e.g. not soft linked from elsewhere**, otherwise your may encounter errors later, and your model deployment may fail. You should assume no external internet access from the docker.

**From now on, you should always run `dynalab-cli` from the root path, otherwise it will get confused and you may see weird errors.**

### Step 2: Complete the model handler
If you don't already have a handler file, we will have created a [template](https://github.com/facebookresearch/dynalab/blob/master/dynalab/handler/handler.py.template) for you with instructions to fill at `./handler.py`. The handler file defines how your model takes inputs, run inference and return response. Follow the instructions in the template file to complete the handler.

For the expected model I/O format of your task, check the definitions [here](dynalab/tasks/README.md).

### Step 3: Quickly check code correctness by local test
Now that you completed the handler file, run a local test to see if your code works correctly.
```
$ dynalab-cli test --local -n <name_of_your_model>
```
If your local test is successful, you'll see "Local test passed" on the prompt. You can then move on to the next step. Otherwise, fix the code according to the error prompt and re-run this step until the output is error free.

### Step 4: Check dependencies by integrated test
The integrated test will run the test inside a mock docker container to simulate the deployment environment. It may take some time to download dependencies in the docker.
```
$ dynalab-cli test -n <name_of_your_model>
```
If the integrated test is successful, you'll see "Integrated test passed" on the prompt. You can then proceed to the next step. Otherwise, please follow the on-screen instructions to check the log and fix your code / dependencies, and repeat this step until the output is error free.

### Step 5: Submit your model
**Make sure you pass the integrated test in Step 4 before submitting the model, otherwise your model deployment might fail.**
You will first need to log in by running
```
$ dynalab-cli login
```
You will be taken to the [Dynabench](www.dynabench.org) website where you'll see an API token (you'll be asked to log in there if you haven't). Click the "Copy" button on the webpage and paste that back in the terminal prompt.

To upload your model, run
```
$ dynalab-cli upload -n <name_of_your_model>
```
Follow the on-screen instructions for uploading the model. After the model is uploaded, it will enter our deployment queue, and you will receive an email when the deployment is done. If deployment is successful, your model will be evaluated on the datasets for that task, and you will be able to see the results on your model page. You can then publish the model for the results to be shown in the leaderboard.

## How do I get help if I run into trouble?
Please create an [issue](https://github.com/facebookresearch/dynalab/issues).
