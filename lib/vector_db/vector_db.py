from abc import ABC, abstractmethod
from typing import List, Dict, Any

class VectorDb(ABC):
    """
    Abstract base class for a Vector Database.
    This allows swapping the underlying vector database implementation.
    """

    @abstractmethod
    def initialize_collection(self, collection_name: str, vector_size: int, distance_metric: str = "cosine") -> None:
        """
        Initialize a collection in the vector database.

        :param collection_name: Name of the collection to initialize.
        :param vector_size: The dimension of the vectors stored in the collection.
        :param distance_metric: The metric to use for similarity search (e.g., cosine, euclidean).
        """
        pass

    @abstractmethod
    def store_vectors(self, collection_name: str, vectors: List[Dict[str, Any]]) -> None:
        """
        Store vectors in the specified collection.

        :param collection_name: Name of the collection to store vectors.
        :param vectors: A list of dictionaries, each containing:
                        - 'id': A unique identifier for the vector.
                        - 'vector': The vector to store.
                        - 'payload': Optional metadata associated with the vector.
        """
        pass

    @abstractmethod
    def search_vectors(self, collection_name: str, query_vector: List[float], top_k: int) -> List[Dict[str, Any]]:
        """
        Search for the most similar vectors in a collection.

        :param collection_name: Name of the collection to search.
        :param query_vector: The query vector to search with.
        :param top_k: Number of top results to return.
        :return: A list of dictionaries representing the search results, each containing:
                 - 'id': The identifier of the matched vector.
                 - 'score': The similarity score.
                 - 'payload': Metadata associated with the matched vector.
        """
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) -> None:
        """
        Delete an entire collection from the vector database.

        :param collection_name: Name of the collection to delete.
        """
        pass

    @abstractmethod
    def retrieve_contexts(self, collection_name: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant contexts based on the query.

        :param collection_name: Name of the collection to search.
        :param query: The query string to embed and search for.
        :param top_k: Number of top results to return.
        :return: A list of dictionaries representing the relevant contexts, each containing:
                 - 'content': The context content (text, image description, or audio transcription).
                 - 'score': The similarity score.
        """
        pass

    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists in the vector database.

        :param collection_name: Name of the collection to check.
        :return: True if the collection exists, False otherwise.
        """
        pass