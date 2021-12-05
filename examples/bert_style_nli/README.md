This directory contains an example handler.py for a Huggingface BERT-style QA
model. It was tested with BERT.

**Here are the steps to use this handler in a Dynalab submission:**


1. Run `intializer.py` to place your trained model files

2. Add a requirements.txt. For the Huggingface ALBERT, the requirements are:
```
transformers
sentencepiece
protobuf
torch
```

***Concretely, you would go through the following steps:***
1. Download a model from huggingface, for example [this one](https://huggingface.co/typeform/distilbert-base-uncased-mnli/tree/main) (download `pytorch_model.bin`, `config.json`, `tokenizer.json`) into this folder (`dynalab/examples/bart`)

2. Make a new file `requirements.txt` and add:
```
transformers
```

3. Set up the project via ```dynalab-cli```, remembering to add the model and
tokenizer files to ```model_files``` with
```dynalab-cli init -n <name of your model> --amend```.

For BERT, these are 
```["config.json", "special_tokens_map.json", "tokenizer_config.json", "vocab.txt"]```.
