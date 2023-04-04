import pickle
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders.directory import DirectoryLoader
from langchain.callbacks import get_openai_callback

import settings
from code_loader import GithubCodeLoader


def ingest_docs():
    """Ingest all docs."""
    loaders = []
    raw_documents = []
    for repo in settings.GIT_REPO_URLS:
        try:
            repo_url, branch = repo
        except:
            repo_url, branch = repo, settings.GIT_DEFAULT_BRANCH

        print(f"Loading {repo_url} with branch {branch}")
        loader = GithubCodeLoader(repo_url, local_dir=settings.GIT_REPOS_DIR, branch=branch, debug=True)
        docs = loader.load()
        if docs:
            print(f"Loaded {len(docs)} documents from {repo_url}")
            raw_documents.extend(docs)

    with get_openai_callback() as cb:
        print(f"Loaded total {len(raw_documents)} documents")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        documents = text_splitter.split_documents(raw_documents)
        embeddings = OpenAIEmbeddings()
        print("Ingesting documents...")
        db = FAISS.from_documents(documents, embeddings)
        # Save vectorstore
        print(f"Saving vectorstore {settings.GIT_FAISS_VECTOR_DATABASE}")
        with open(settings.GIT_FAISS_VECTOR_DATABASE, "wb") as f:
            pickle.dump(db, f)
        print(f"Total Tokens: {cb.total_tokens}")
        print(f"Prompt Tokens: {cb.prompt_tokens}")
        print(f"Completion Tokens: {cb.completion_tokens}")
        print(f"Successful Requests: {cb.successful_requests}")
        print(f"Total Cost (USD): ${cb.total_cost}")



if __name__ == "__main__":
    ingest_docs()

