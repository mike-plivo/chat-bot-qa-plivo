import sys
import pickle
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit import prompt
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain

import settings


messages = [
    SystemMessagePromptTemplate.from_template(settings.GIT_SYSTEM_TEMPLATE),
    HumanMessagePromptTemplate.from_template("{question}")
]
chat_prompt = ChatPromptTemplate.from_messages(messages)

with open(settings.GIT_FAISS_VECTOR_DATABASE, "rb") as f:
    db = pickle.load(f)

chain_type_kwargs = {"prompt": chat_prompt}
llm = ChatOpenAI(model_name=settings.GIT_OPENAI_MODEL, 
                 temperature=settings.GIT_OPENAI_TEMPERATURE, 
                 max_tokens=settings.GIT_OPENAI_MAX_TOKENS)
chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever(),
    return_source_documents=True,
    chain_type_kwargs=chain_type_kwargs
)

def print_result(result):
    cr = "\n"
    output_text = f"""
## Question
{query}

## Answer
{result['answer']}

## References
{cr.join(list(set([doc.metadata['source'] for doc in result['source_documents']])))}

## Debug
{result}

"""
    print(output_text)


while True:
    try:
        print_formatted_text(HTML('<p fg="ansiwhite">Enter your coding question</p><p fg="ansired"> ("quit" to exit)</p>'))
        query = prompt(">>> ")
        if query == "quit":
            sys.exit(0)
        if not query:
            continue
        result = chain(query)
        print_result(result)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(0)
