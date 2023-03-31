import pickle
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders.sitemap import SitemapLoader

import settings

def ingest_docs():
    """Get documents from web pages."""
    loader = SitemapLoader(web_path=settings.SITEMAP_URL)
    raw_documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(documents, embeddings)

    # Save vectorstore
    with open(settings.FAISS_VECTOR_DATABASE , "wb") as f:
        pickle.dump(db, f)


if __name__ == "__main__":
    ingest_docs()
