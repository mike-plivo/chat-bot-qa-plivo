# chat-bot-qa-plivo
Chat Bots for Plivo APIs and SDKs.

*CodeBot: This Q&A bot is designed to provide coding implementation answers to user questions using information extracted from the Plivo APIs and SDKs. 

*FAQBot: This Q&A bot is designed to answer to user questions using information extracted from the Plivo documentation, APIs and SDKs. 

It utilizes the OpenAI GPT-3.5-turbo model and a pre-built FAISS vector database to search for relevant information and answer user questions in a concise and accurate manner.

You can ingest Github repositories and websites (via sitemap) into The FAISS vector database.

## Installation

```bash
pip3 install -r requirements.txt
```

## Configure environment variable OPENAI_API_KEY

```bash
export OPENAI_API_KEY=sk-xxxx
```

## Build the FAISS vector database
Add the git repositories you want to scan in settings.py, then execute the following command:
```bash
python3 ingest.py
```

## Usage CodeBot

```bash
python3 -m codebot -h
```

### CLI mode
```bash
python3 -m codebot -c python -m cli -a 'send an SMS'
```

You can also use stdin for the -a/--ask option:
```bash
echo 'send an SMS' |python3 -m codebot -d -c python -m cli -a -
```

### Prompt mode
```bash
python3 -m codebot -c python
```

- Use the `/help` command in Prompt mode for help.

### Debug mode
Use the `-d` option to enable debug mode.

### Use a Python module
```python
from codebot import CodeBot
bot = CodeBot()
bot.set_debug(True)
result = bot.ask(code="python", question="send an SMS")
print(result)
```

## Usage FAQBot

```bash
python3 -m faqbot -h
```

### CLI mode
```bash
python3 -m faqbot -m cli -a 'How to send an SMS?'
```

You can also use stdin for the -a/--ask option:
```bash
echo 'How to send an SMS?' |python3 -m faqbot -d -c python -m cli -a -
```

### Prompt mode
```bash
python3 -m faqbot
```

- Use the `/help` command in Prompt mode for help.

### Debug mode
Use the `-d` option to enable debug mode.

### Use a Python module
```python
from faqbot import FAQBot
bot = FAQBot()
bot.set_debug(True)
result = bot.ask(question="How to send an SMS?")
print(result)
```

## Notes
- If the bot does not know the answer, it will respond with "I don't know" and will not attempt to make up an answer.

