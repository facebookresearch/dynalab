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
