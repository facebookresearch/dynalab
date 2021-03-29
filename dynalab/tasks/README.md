# Model I/O

For each task in Dynabench, the expected input and output format is pre-defined. Both the input and output are json objects, and your model should always expect a single example as the input (i.e. no batching).

## Input
To view the input format of a task, in a python interpreter, do
```
>>> from dynalab.tasks import nli # or hs, sentiment, qa
>>> print(nli.TaskIO().data)
```
The input will always have the same attributes.

## Output
To view the expected output format, in a python interpreter, do
```
>>> from dynalab.tasks import nli # or hs, sentiment, qa
>>> print(nli.TaskIO().verify_response.__doc__)
```
For currently existing tasks, the output format is expected to be

**nli**
```
{
    "id": copy from input["uid"],
    "label": "c" | "e" | "n"
}
```
**hs**
```
{
    "id": copy from input["uid"],
    "label": "hate" | "nohate"
}
```
**sentiment**
```
{
    "id": copy from input["uid"],
    "label": "positive" | "negative" | "neutral"
}
```
**qa**
```
{
    "id": copy from input["uid"],
    "answer": the answer string extracted from input["context"]
}
```
