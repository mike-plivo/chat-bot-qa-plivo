import os
import sys
from langchain.document_loaders.sitemap import SitemapLoader

from code_loader import GithubCodeLoader
from sitemapchunk_loader import SitemapChunkLoader
from vectordb import Ingestor
import settings


def ingest_docs_from_github_repos():
    """Ingest all docs."""
    repos = []
    ingested_docs = 0
    if not settings.CODEBOT_GIT_REPO_URLS:
        print("No repos specified in settings.CODEBOT_GIT_REPO_URLS")
        return ingested_docs

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
            print(f"Loaded {len(docs)} documents from {sitemap_url}")
            ingested_docs += len(docs)
            Ingestor.ingest(settings.VECTOR_DATABASE, docs, overwrite=False)
            continue
    return ingested_docs


def ingest_docs_from_sitemaps():
    ingested_docs = 0
    if not settings.CODEBOT_SITEMAP_URLS:
        print("No sitemap urls specified in settings.CODEBOT_SITEMAP_URLS")
        return ingested_docs

    for sitemap_url in settings.CODEBOT_SITEMAP_URLS:
        print(f"Loading {sitemap_url}")
        loader = SitemapChunkLoader(web_path=sitemap_url)
        while True:
            docs = loader.load_chunks(chunk_size=100)
            if len(docs) > 0:
                print(f"Loaded {len(docs)} documents from {sitemap_url}")
                ingested_docs += len(docs)
                Ingestor.ingest(settings.VECTOR_DATABASE, docs, overwrite=False)
                continue
            break
    return ingested_docs


def ingest_all_docs():
    """Ingest all docs."""
    k = os.getenv("OPENAI_API_KEY")
    if not k:
        print("OPENAI_API_KEY not set")
        sys.exit(1)
    if not settings.VECTOR_DATABASE:
        print("VECTOR_DATABASE not set")
        sys.exit(1)
    if os.path.exists(settings.VECTOR_DATABASE):
        print(f"Database {settings.VECTOR_DATABASE} already exists. Delete it first if you want to re-ingest")
        sys.exit(1)
    ingested_docs = ingest_docs_from_sitemaps()
    ingested_docs += ingest_docs_from_github_repos()
    print(f"Ingested total {ingested_docs} documents")


if __name__ == "__main__":
    ingest_all_docs()

