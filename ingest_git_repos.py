import os
import subprocess
import pickle
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders.directory import DirectoryLoader

import settings


def clone_git_repo(repo_url, branch="master"):
    """Clone a git repo."""
    repo_name = repo_url.split("/")[-1]
    repo_path = os.path.join(settings.GIT_REPOS_DIR, repo_name)
    # Check if repo exists and pull
    if os.path.isdir(repo_path):
        print(f"Pulling repo: {repo_url} with branch: {branch}")
        # use Popen to avoid blocking
        cmd = f"git pull"
        exitcode, output = subprocess.getstatusoutput(cmd)
        if exitcode != 0:
            raise Exception(f"Error cloning repo: exitcode {exitcode}: {output}")
    # If repo doesn't exist, clone
    else:
        print(f"Cloning repo: {repo_url} with branch: {branch}")
        # use Popen to avoid blocking
        cmd = f"git clone {repo_url} -b {branch} --single-branch {repo_path}"
        exitcode, output = subprocess.getstatusoutput(cmd)
        if exitcode != 0:
            raise Exception(f"Error cloning repo: exitcode {exitcode}: {output}")
    return repo_path

def clone_all_git_repos():
    """Clone all git repos."""
    repo_paths = []
    for repo in settings.GIT_REPO_URLS:
        try:
            repo_url, branch = repo
        except:
            repo_url = repo
            branch = "master"

        repo_path = clone_git_repo(repo_url)
        repo_paths.append(repo_path)
    return repo_paths

def ingest_docs():
    """Ingest all docs."""
    # Clone all repos
    clone_all_git_repos()
    print("Cloned all repos, loading documents...")
    # TODO use custom CodeLoader !!!
    loader = DirectoryLoader(path=settings.GIT_REPOS_DIR, load_hidden=True, recursive=True)
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings()
    print("Ingesting documents...")
    db = FAISS.from_documents(documents, embeddings)

    # Save vectorstore
    print("Saving vectorstore ...")
    with open(settings.GIT_FAISS_VECTOR_DATABASE,"wb") as f:
        pickle.dump(db, f)


if __name__ == "__main__":
    ingest_docs()

