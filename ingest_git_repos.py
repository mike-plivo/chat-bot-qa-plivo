import sys
import pickle
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders.directory import DirectoryLoader

import settings
from code_loader import GithubCodeLoader


def ingest_docs():
    """Ingest all docs."""
    repos = []
    loaders = []
    raw_documents = []
    for repo in settings.CODEBOT_GIT_REPO_URLS:
        try:
            repo_url, branch = repo
            repos.append(i(repo_url, branch))
        except:
            print(f"Invalid repo {repo}. Format should be (repo_url, branch)")
            sys.exit(1)

    for repo_url, branch in repos:
        print(f"Loading {repo_url} with branch {branch}")
        loader = GithubCodeLoader(repo_url, local_dir=settings.CODEBOT_GIT_REPOS_DIR, branch=branch, debug=True)
        docs = loader.load()
        if docs:
            print(f"Loaded {len(docs)} documents from {repo_url}")
            raw_documents.extend(docs)

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
    print(f"Saving vectorstore {settings.CODEBOT_FAISS_VECTOR_DATABASE}")
    with open(settings.CODEBOT_FAISS_VECTOR_DATABASE, "wb") as f:
        pickle.dump(db, f)



if __name__ == "__main__":
    ingest_docs()

