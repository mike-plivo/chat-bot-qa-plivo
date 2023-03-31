# chat-bot-qa-plivo
Chat Bot Q&amp;A Plivo

This Q&A bot is designed to provide answers to user questions using information extracted from Plivo's sitemap. It utilizes the OpenAI GPT-3.5-turbo model and a pre-built FAISS vector database to search for relevant information and answer user questions in a concise and accurate manner.

## Installation

```bash
pip3 install -r requirements.txt
```

## Configure environment variable OPENAI_API_KEY

```bash
export OPENAI_API_KEY=sk-xxxx
```

## Configure settings.py

The following variables are used for configuration:

- `SITEMAP_URL`: The URL to the sitemap.xml file used as the source for indexing and searching. (e.g., "https://plivo.com/sitemap.xml")
- `FAISS_VECTOR_DATABASE`: The path to the FAISS vector database file containing the pre-built index of the sitemap. (e.g., "data/plivo_com.faiss")
- `SYSTEM_TEMPLATE`: The template used for generating answers based on the context provided by the search results. Make sure to include source information in the answer using the format "SOURCES: source1 source2".
- `CHAT_OPENAI_MODEL`: The OpenAI model used for generating answers. (e.g., "gpt-3.5-turbo")
- `CHAT_OPENAI_TEMPERATURE`: Controls the randomness of the model's output. Set to 0.0 for deterministic answers.
- `CHAT_OPENAI_MAX_TOKENS`: The maximum number of tokens (words and characters) allowed in the generated answer. (e.g., 1000)

## Usage

To use the Q&A bot, provide a user question as input. The bot will search for relevant information, generate an answer based on the context and sources, and return the answer to the user.
```bash
python3 chatbot-cli.py
```

## Example

User question: "How do I send an SMS using Plivo's API?"

The bot will search the sitemap for relevant information, use the SYSTEM_TEMPLATE to construct an answer that includes the sources, and return the answer:

Answer: "To send an SMS using Plivo's API, follow these steps: [step-by-step instructions]. SOURCES: https://plivo.com/docs/sms/send-sms"

## Notes

- If the bot does not know the answer, it will respond with "I don't know" and will not attempt to make up an answer.
- The quality of the answers depends on the accuracy and comprehensiveness of the sitemap.xml file and the pre-built FAISS vector database.

