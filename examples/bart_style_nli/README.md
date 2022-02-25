This directory contains an example handler.py for a Huggingface BART-style NLI model. 

***How to customize initializer:***
1. Since we are using BartModel specifically [this one](https://huggingface.co/facebook/bart-base/tree/main), we imported BartTokenizer, BartModel, if you are using BART istead you can import BertTokenizer, BertModel.

2. Change *bart-base* in `model = BartModel.from_pretrained('facebook/bart-base')` to be the name of your chosen model from HuggingFace, do the same for `tokenizer = BartTokenizer.from_pretrained('facebook/bart-base')`

***Here are the following steps to use this handler:***

1. Run `intializer.py` and it would essentially download all the required files namely `pytorch_model.bin`, `config.json`, `special_tokens_map.json`, `vocab.json` and `tokenizer_config.json` into this folder (`dynalab/examples/bart_style_nli`)

2. Make a new file `requirements.txt` and add:
```
transformers
sentencepiece
protobuf
```

3. Run `dynalab-cli init -n bartstylenli`, and provide these answers:

```
Initializing . for dynalab model 'bartstylenli'...
Please choose a valid task name from one of [nli, qa, sentiment, hs, vqa, flores_small1, flores_small2, flores_full]: nli
Checkpoint file ./checkpoint.pt not a valid path. Please re-specify path to checkpoint file inside the root dir: pytorch_model.bin
Handler file found at ./handler.py. Press enter, or specify alternative path [./handler.py]: 
Requirements file found. Do you want us to install dependencies using ./requirements.txt? [Y/n] Y
```

4. Run `dynalab-cli init -n bartstylenli --amend` and fill `model_files` with `["vocab.json", "tokenizer_config.json", "config.json", "special_tokens_map.json"]`.

5. Run tests:
```
dynalab-cli test --local -n bartstylenli # this should pass
dynalab-cli test -n bartstylenli # this should pass (try increasing Docker storage size and memory if it does not)
```

6. Login into Dynabench via `dynalab-cli login` and then submit the model via `dynalab-cli upload -n bartstylenli`