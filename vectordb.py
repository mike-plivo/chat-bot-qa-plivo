import os
import pickle
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
        print(f"Ingesting {len(self.docs)} documents ...")
        if self.vector_url[:8] == "redis://":
            return self._ingest_redis()
        return self._ingest_faiss()

    def _ingest_redis(self):
        while len(self.docs) > 0:
            docs = self._pop()
            print(f"Saving {len(docs)} into Redis {self.vector_url}")
            r = Redis.from_documents(docs, self.embeddings, redis_url=self.vector_url, index_name='link')
        return True

    def _ingest_faiss(self):
        idx = 1
        print(f"Total documents to process: {len(self.docs)}")
        while len(self.docs) > 0:
            print(f"Total documents left to process: {len(self.docs)}")
            docs = self._pop()
            print(f"Processing {len(docs)} documents...")
            db = FAISS.from_documents(docs, self.embeddings)
            vector_url = self.vector_url + f".{idx}"
            print(f"Saving {len(docs)} documents into FAISS {vector_url}")
            with open(vector_url, "wb") as f:
                pickle.dump(db, f)
            idx += 1
            print(f"Saved {len(docs)} documents into FAISS {vector_url}")
            print(f"Processed {len(docs)} documents...")
        
        orig_vector_url = self.vector_url + ".1"
        db = Loader.load(orig_vector_url)
        for i in range(1, idx):
            vector_url = self.vector_url + f".{i}"
            print(f"Merging {vector_url} into {orig_vector_url}")
            db.merge_from(Loader.load(vector_url))
            os.remove(vector_url)
            print(f"Merged {vector_url} into {orig_vector_url}")

        print(f"Saving merged FAISS into {self.vector_url}")
        try: os.remove(self.vector_url)
        except: pass
        try: os.remove(orig_vector_url)
        except: pass
        with open(self.vector_url, "wb") as f:
            pickle.dump(db, f)
        return True
    
    def run(self):
        return self._ingest()

    def _pop(self, size=500):
        docs = []
        i = 0
        while i < size:
            try:
                doc = self.docs.pop()
                docs.append(doc)
                i += 1
            except IndexError:
                break
        return docs

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
        if not os.path.exists(self.vector_url):
            raise Exception(f"FAISS file not found: {self.vector_url}")
        print(f"Loading FAISS {self.vector_url}")
        with open(self.vector_url, "rb") as f:
            db = pickle.load(f)
        print(f"Loaded FAISS {self.vector_url}")
        return db

    def run(self):
        return self._load()

    @classmethod
    def load(cls, vector_url):
        return cls(vector_url).run()

