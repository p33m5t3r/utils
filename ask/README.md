# ask


a simple cli interface to query chatgpt from your terminal

supports piped input, pulling in files as context, 
and keeps the last chat in a json text buffer.


```
usage: ask.py [-h] [-r] [-t] [-v] [-c CONTEXT [CONTEXT ...]] message

ask an llm a question

positional arguments:
  message               message

options:
  -h, --help            show this help message and exit
  -r, --resume          resume conversation
  -t, --temp            dont store convo
  -v, --verbose         be verbose
  -c CONTEXT [CONTEXT ...], --context CONTEXT [CONTEXT ...]
                        list of context files
```

## installation

1. edit the first line of `ask.py` to point at a python installation that has openai pip-installed
2. `chmod +x ask.py`
3. `sudo mv ask.py /usr/local/bin/ask`

## TODO

add support for local llm
