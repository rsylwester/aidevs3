import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams


# Initialize Qdrant Collection
def init_qdrant_collection(collection_name, vector_size):
    qdrant = QdrantClient(url="http://localhost:6333")  # Update for cloud instance
    qdrant.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance="Cosine")
    )
    print(f"Initialized Qdrant collection: {collection_name}")
