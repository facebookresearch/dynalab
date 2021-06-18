This directory contains an example handler.py for a Huggingface ELECTRA-style QA
model. It was tested with ELECTRA.

**Here are the steps to use this handler in a Dynalab submission:**

1. In this directory, place your trained model files
(the .bin file and the config.json) and tokenizer files
(for ELECTRA, this is special_tokens_map.json,
tokenizer_config.json and vocab.txt).

2. Add the provided requirements.txt file.

3. Set up the project via ```dynalab-cli```, remembering to add the model and
tokenizer files to ```model_files``` with
```dynalab-cli init -n <name of your model> --amend```.
