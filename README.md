# chat-bot-qa-plivo
Chat Bot for Plivo APIs and SDKs.

This Q&A bot is designed to provide coding implementation answers to user questions using information extracted from Plivo APIs and SDKs. 

It utilizes the OpenAI GPT-3.5-turbo model and a pre-built FAISS vector database to search for relevant information and answer user questions in a concise and accurate manner.

You can ingest Github repositories into The FAISS vector database.

## Installation

```bash
pip3 install -r requirements.txt
```

## Configure environment variable OPENAI_API_KEY

```bash
export OPENAI_API_KEY=sk-xxxx
```

## Usage

To use the Q&A bot, provide a user question as input. The bot will search for relevant information, generate an answer based on the context and sources, and return the answer to the user.
```bash
python3 code-bot-cli.py -h
```

## Examples

### CLI mode
```bash
python3 code-bot-cli.py -c python -m cli -a 'send an SMS'
```

### Prompt mode
```bash
python3 code-bot-cli.py -c python
```

### Debug mode
Use the `-d` option to enable debug mode.

## Building the FAISS vector database
Add the git repositories you want to scan in settings.py, then execute the following command:
```bash
python3 ingest_git_repos.py
```

## Notes

- If the bot does not know the answer, it will respond with "I don't know" and will not attempt to make up an answer.

