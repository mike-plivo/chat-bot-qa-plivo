import os
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

def qdrant_keepalive():
    HITS = 5
    vector_url = os.environ.get("VECTOR_DATABASE", None)
    url = vector_url.replace("qdrant://", "") or None
    api_key = os.environ.get("QDRANT_API_KEY", None)
    if not url:
        raise ValueError("Qdrant URL is required")
    if not api_key:
        raise ValueError("Qdrant API key is required")
    client = QdrantClient(url=url, api_key=api_key)
    client.recreate_collection(
        collection_name="test_collection",
        vectors_config=VectorParams(size=10, distance=Distance.COSINE),
    )
    vectors = np.random.rand(10, 10)
    client.upsert(
        collection_name="test_collection",
        points=[
            PointStruct(
                id=idx,
                vector=vector.tolist(),
                payload={"color": "red", "rand_number": idx % 10}
            )
            for idx, vector in enumerate(vectors)
        ]
    )
    query_vector = np.random.rand(10)
    hits = client.search(
        collection_name="test_collection",
        query_vector=query_vector,
        limit=HITS  # Return 5 closest points
    )
    client.delete_collection(collection_name="test_collection")
    if len(hits) != HITS:
        raise ValueError("Qdrant Keepalive: Wrong number of hits")
    return True

if __name__ == "__main__":
    try:
        qdrant_keepalive()
        exit(0)
    except Exception as e:
        print("Qdrant Keepalive: Error: {}".format(e))
        exit(1)


