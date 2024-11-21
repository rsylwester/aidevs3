from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, PointStruct

from openai_client import OpenAIClient
from .vector_db import VectorDb

openai_client = OpenAIClient()


class QdrantDb(VectorDb):
    def __init__(self, url: str = "http://localhost:6333"):
        """
        Initialize the Qdrant client.

        :param url: URL of the Qdrant instance.
        """
        self.client = QdrantClient(url=url)

    def initialize_collection(self, collection_name: str, vector_size: int = 1536, distance_metric: str = "cosine",
                              recreate=False) -> None:
        """
        Initialize a collection in Qdrant.
        """

        if self.collection_exists(collection_name=collection_name):
            if recreate:
                self.delete_collection(collection_name=collection_name)
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=distance_metric.capitalize())
                )
        else:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance_metric.capitalize())
            )

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists in Qdrant.
        """
        try:
            collections = self.client.get_collections().collections
            return any(collection.name == collection_name for collection in collections)
        except Exception as e:
            print(f"Error checking collection existence: {e}")
            return False

    def is_collection_empty(self, collection_name: str) -> bool:
        """
        Check if a Qdrant collection is not empty.

        :param collection_name: Name of the collection to check.
        :return: True if the collection is not empty, False otherwise.
        """
        try:
            collection_info = self.client.get_collection(collection_name)
            return collection_info.points_count == 0
        except Exception as e:
            print(f"Error checking if collection is not empty: {e}")
            return False

    def store_vectors(self, collection_name: str, vectors: List[Dict[str, Any]]) -> None:
        """
        Store vectors in Qdrant.
        """
        points = [
            PointStruct(
                id=vector["id"],
                vector=vector["vector"],
                payload=vector.get("payload", {})
            )
            for vector in vectors
        ]
        self.client.upsert(collection_name=collection_name, points=points)

    def search_vectors(self, collection_name: str, query_vector: List[float], top_k: int) -> List[Dict[str, Any]]:
        """
        Search vectors in Qdrant.
        """
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        return [
            {"id": result.id, "score": result.score, "payload": result.payload}
            for result in results
        ]

    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection in Qdrant.
        """
        self.client.delete_collection(collection_name=collection_name)

    def retrieve_contexts(self, collection_name: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Embed the query and retrieve relevant contexts (text, images, or audio) from Qdrant.
        """
        # Generate the query embedding
        query_vector = openai_client.embed_text(query)

        # Retrieve the top-k most relevant vectors from Qdrant
        results = self.search_vectors(collection_name, query_vector, top_k)

        # Format the results to include content and relevance score
        return [
            {"content": result["payload"].get("content", ""), "filename": result["payload"].get("filename", ""),
             "score": result["score"]}
            for result in results
        ]
