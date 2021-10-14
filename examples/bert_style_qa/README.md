This directory contains an example handler.py for a Huggingface BERT-style QA
model. It was tested with ALBERT.

**Here are the steps to use this handler in a Dynalab submission:**

1. In this directory, place your trained model files
(the .bin file and the config.json) and tokenizer files
(for ALBERT, this is special_tokens_map.json, spiece.model, and
tokenizer_config.json).

2. Add a requirements.txt. For the Huggingface ALBERT, the requirements are:
```
transformers
sentencepiece
protobuf
```

3. Set up the project via ```dynalab-cli```, remembering to add the model and
tokenizer files to ```model_files``` with
```dynalab-cli init -n <name of your model> --amend```.

***If you just want to get an example submitted to Dynabench for the QA task***
1. Download a model from huggingface, for example [this one](https://huggingface.co/distilbert-base-cased-distilled-squad/tree/main) (download `pytorch_model.bin`, `config.json`, `tokenizer.json`, and `tokenizer_config.json`) into this folder (`dynalab/examples/bert_style_qa`)

2. Make a new file `requirements.txt` and add:
```
transformers
```

3. Run `dynalab-cli init -n bertstyleqa`, and follow these answers:

```
Initializing . for dynalab model 'bertstyleqa'...
Please choose a valid task name from one of [nli, qa, sentiment, hs, vqa, flores_small1, flores_small2, flores_full]: qa
Checkpoint file ./checkpoint.pt not a valid path. Please re-specify path to checkpoint file inside the root dir: pytorch_model.bin
Handler file found at ./handler.py. Press enter, or specify alternative path [./handler.py]: 
Requirements file found. Do you want us to install dependencies using ./requirements.txt? [Y/n] Y
```

4. Run `dynalab-cli init -n bertstyleqa --amend` and fill `model_files` with `["tokenizer.json", "tokenizer_config.json", "config.json"]`

5. Run tests:
```
dynalab-cli test --local -n bertstyleqa # this should pass
dynalab-cli test -n bertstyleqa # this should pass (try increasing Docker storage size and memory if it does not)
```

6. Login into Dynabench via `dynalab-cli login` and then submit the model via `dynalab-cli upload -n bertstyleqa`

