## Description

This tool uses Whisper to transcribe videos and audios. 

## Installation instructions


```pip install poetry
poetry shell
poetry build
poetry install
```




This creates a specific environment with all the libraries in need!

``` To specify configurations use .env file ```

## Configuration
configure the .env file might like this:

```
OPENAI_API_KEY= openai api key...
OPENAI_MODEL = model to be used
PROJECT_ROOT =  root folder of project
REQUEST_TIMEOUT = 300
LLM_CACHE = False
VERBOSE_LLM = True
TOKEN_LIMIT = 13000
```

