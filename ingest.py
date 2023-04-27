import os
import sys
from langchain.document_loaders.sitemap import SitemapLoader

from code_loader import GithubCodeLoader
from vectordb import Ingestor
import settings


def ingest_docs_from_github_repos():
    """Ingest all docs."""
    repos = []
    loaders = []
    raw_documents = []
    if not settings.CODEBOT_GIT_REPO_URLS:
        print("No repos specified in settings.CODEBOT_GIT_REPO_URLS")
        return raw_documents

    for repo in settings.CODEBOT_GIT_REPO_URLS:
        try:
            repo_url, branch = repo
            repos.append((repo_url, branch))
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
    return raw_documents


def ingest_docs_from_sitemaps():
    loaders = []
    raw_documents = []
    if not settings.CODEBOT_SITEMAP_URLS:
        print("No sitemap urls specified in settings.CODEBOT_SITEMAP_URLS")
        return raw_documents

    for sitemap_url in settings.CODEBOT_SITEMAP_URLS:
        print(f"Loading {sitemap_url}")
        loader = SitemapLoader(web_path=sitemap_url)
        docs = loader.load()
        if docs:
            print(f"Loaded {len(docs)} documents from {sitemap_url}")
            raw_documents.extend(docs)
    return raw_documents

def ingest_all_docs():
    """Ingest all docs."""
    k = os.getenv("OPENAI_API_KEY")
    if not k:
        print("OPENAI_API_KEY not set")
        sys.exit(1)
    docs = []
    docs.extend(ingest_docs_from_sitemaps())
    docs.extend(ingest_docs_from_github_repos())

    print(f"Loaded total {len(docs)} documents")
    Ingestor.ingest(settings.CODEBOT_VECTOR_DATABASE, docs)


if __name__ == "__main__":
    ingest_all_docs()

