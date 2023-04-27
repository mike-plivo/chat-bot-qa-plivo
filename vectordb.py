from langchain.vectorstores.faiss import FAISS
from langchain.vectorstores.redis import Redis
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

class Ingestor(object):
    def __init__(self, vector_url, docs):
        self.vector_url = vector_url
        self.embeddings = OpenAIEmbeddings()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        self.docs = text_splitter.split_documents(docs)

    def _ingest(self):
        print("Ingesting documents...")
        if self.vector_url[:8] == "redis://":
            return self._ingest_redis()
        return self._ingest_faiss()

    def _ingest_redis(self):
        print(f"Saving into Redis {self.vector_url}")
        r = Redis.from_documents(self.docs, self.embeddings, redis_url=self.vector_url, index_name='link')
        return True

    def _ingest_faiss(self):
        db = FAISS.from_documents(self.docs, self.embeddings)
        print(f"Saving into FAISS {self.vector_url}")
        with open(self.vector_url, "wb") as f:
            pickle.dump(db, f)
        return True

    def run(self):
        return self._ingest()

    @classmethod
    def ingest(cls, vector_url, docs):
        return cls(vector_url, docs).run()
        


class Loader(object):
    def __init__(self, vector_url):
        self.vector_url = vector_url

    def _load(self):
        #print("Loading documents...")
        if self.vector_url[:8] == "redis://":
            return self._load_redis()
        return self._load_faiss()

    def _load_redis(self):
        #print(f"Loading from Redis {self.vector_url}")
        embeddings = OpenAIEmbeddings()
        r = Redis.from_existing_index(embeddings, redis_url=self.vector_url, index_name='link')
        return r

    def _load_faiss(self):
        #print(f"Loading from FAISS {self.vector_url}")
        with open(self.vector_url, "rb") as f:
            db = pickle.load(f)
        return db

    def run(self):
        return self._load()

    @classmethod
    def load(cls, vector_url):
        return cls(vector_url).run()

