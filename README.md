xorius
======

A LLM-based agent

## Installation

```shell
pip install xorius
```

## Usage

```
Usage: xorius-cli [OPTIONS]

Options:
  --api-key TEXT        [required]
  --temperature FLOAT   [default: 0.7]
  --max-tokens INTEGER  [default: 512]
  --proxy TEXT
  --help                Show this message and exit.
```

e.g.:

```shell
xorius-cli --api-key <YOUR OPENAI API KEY> \
           --temperature 0.7 \
           --max-tokens 512 \
           --proxy http://localhost:8080
```
