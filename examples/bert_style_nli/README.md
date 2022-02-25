This directory contains an example handler.py for a Huggingface BERT-style NLI
model. 

**Here are the steps to use this handler in a Dynalab submission:**


1. n this directory, place your trained model files (the .bin file and the config.json) and tokenizer files (special_tokens_map.json, and tokenizer_config.json). **Or** Run `intializer.py` to use the trained model files used in this example

2. Add a requirements.txt. For the Huggingface BERT, the requirements are:
```
transformers
sentencepiece
protobuf
torch
```

***How to customize initializer:***
1. Since we are using BertModel, we imported BertTokenizer, BertConfig, BertModel, if you are using BART istead you can import BartTokenizer, BartConfig, BartModel

2. Change *bert-base-uncased* in `model = BertModel.from_pretrained('bert-base-uncased')` to be the name of your chosen model from HuggingFace, do the same for `tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')`

***Initialize Dynalab***
1. Set up the project via ```dynalab-cli```, remembering to add the model and
tokenizer files to ```model_files``` with
```dynalab-cli init -n <name of your model> --amend```.

For BERT, these are 
```["config.json", "special_tokens_map.json", "tokenizer_config.json", "vocab.txt"]```.

2. Run `dynalab-cli init -n bertstylenli`, and provide these answers:

```
Initializing . for dynalab model 'bertstylenli'...
Please choose a valid task name from one of [nli, qa, sentiment, hs, vqa, flores_small1, flores_small2, flores_full]: nli
Checkpoint file ./checkpoint.pt not a valid path. Please re-specify path to checkpoint file inside the root dir: pytorch_model.bin
Handler file found at ./handler.py. Press enter, or specify alternative path [./handler.py]: 
Requirements file found. Do you want us to install dependencies using ./requirements.txt? [Y/n] Y
```

4. Run `dynalab-cli init -n bertstylenli --amend` and fill `model_files` with `["tokenizer.json", "tokenizer_config.json", "config.json"]`

***Test and Upload your model using Dynalab***
5. Run tests:
```
dynalab-cli test --local -n bertstylenli # this should pass
dynalab-cli test -n bertstylenli # this should pass (try increasing Docker storage size and memory if it does not)
```

6. Login into Dynabench via `dynalab-cli login` and then submit the model via `dynalab-cli upload -n bertstylenli`