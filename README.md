## What is Dynalab?
Imagine you developed a fancy model, living in `/path/to/fancy_project`, and you want to share your amazing results on the [Dynabench](www.dynabench.org) model leaderboard. Dynalab makes it easy for you to do just that.
## Installation

```
git clone https://github.com/facebookresearch/dynalab.git
cd dynalab
pip install -e .
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

**Beta testing: please copy the `dynalab` directory into your root path**
```
cp -r dynalab /path/to/fancy_project
```

### Step 2: Complete the model handler
If you don't already have a handler file, we will have created a [template](https://github.com/facebookresearch/dynalab/blob/master/dynalab/handler/handler.py.template) for you with instructions to fill at `./handler.py`. The handler file defines how your model takes inputs, runs inference and returns a response. Follow the instructions in the template file to complete the handler.

For the expected model I/O format of your task, check the definitions [here](dynalab/tasks/README.md).

### Step 3: Quickly check correctness by local test
Now that you completed the handler file, run a local test to see if your code works correctly.
```
$ dynalab-cli test --local -n <name_of_your_model>
```
If your local test is successful, you'll see "Local test passed" on the prompt. You can then move on to the next step. Otherwise, fix your project according to the error prompt and re-run this step until the output is error free.

**Exclude large files / folders**
You may get an error if your project folder is too big (e.g. more than 2GB). You can reduce its size by excluding files / folders that are not relevant to your model (e.g. unused checkpoints). To do this, add the paths to the files / folders that you want to exclude into the config by running `dynalab-cli init -n <name_of_your_model> --amend` and update the `exclude` entry, e.g.
```
{
    "exclude": ["checkpoints_folder", "config/irrelevant_config.txt"]
}
```
Remember not to exclude files / folders that are used by your model.

### Step 4: Check dependencies by integrated test
The integrated test will run the test inside a mock docker container to simulate the deployment environment. It may take some time to download dependencies in the docker.
```
$ dynalab-cli test -n <name_of_your_model>
```
If the integrated test is successful, you'll see "Integrated test passed" on the prompt. You can then proceed to the next step. Otherwise, please follow the on-screen instructions to check the log and fix your code / dependencies, and repeat this step until the output is error free.

**Third party libraries**
If your code uses third-party libraries, you may specify them via either `requirements.txt` or `setup.py`. Then call `dynalab-cli init -n <name_of_your_model> --amend` to update the corresponding entry in the config file
  ```
  {
      "requirements": true | false, # true if installing dependencies using requirements.txt
      "setup": true | false # true if installing dependencies using setup.py
  }
  ```
  Some common libraries are pre-installed so you do not need to include them in your requirements.txt or setup.py, unless you need a different version. Please check the [dockerfile](dynalab/dockerfiles/prod/Dockerfile) for the supported libraries. At the moment, supported libraries include
```
torch==1.7.1
```

**Extra model files**
There may be a config file, or self-defined modules that you want to read or import in your handler. There are two ways to do this.
1. Include these files in the dynalab config and read / import them directly without worrying about paths. This also means that all file structure will be flattened. Firstly, run `dynalab-cli init -n <name_of_your_model> --amend` and fill the `model_files` list with the list of file paths inside the root directory, e.g.
   ```
   {
       "model_files": ["configs/model_config.json", "src/my_model.py"]
   }
   ```
   Then in the handler, to read a file, you can read the config by its name, i.e. no path needs to be specified
   ```
   config = json.load("model_config.json")
   ```
   and directly import the module by its name, i.e. no path needs to be specified
   ```
   import my_model
   ```
   We recommend using this method to read files (e.g. configs, vocabularies) which is often flat-structured by its nature.
2. If you do not want to flatten the file structure (e.g. there may be too many dependencies involved), you do not need to add them to the dynalab config. First of all, notice there is a `ROOTPATH` variable available in your handler template. Suppose the file locations are the same as those specified above (`configs/model_config.json` and `src/my_model.py`), you will read the config by
   ```
   config = json.load(os.path.join(ROOTPATH, "configs", "model_config.json"))
   ```
   and import the module by
   ```
   import sys
   sys.path.append(ROOTPATH) # you can uncomment this line in the handler template
   from src import my_model
   ```
   We recommend using this method for importing self-defined modules.

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
