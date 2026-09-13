import chromadb
from chromadb.utils import embedding_functions
from src.config import settings

class VectorStore:
    def __init__(self, persist_directory="./data/chroma"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="historical_resolutions",
            embedding_function=self.embedding_fn
        )

    def add_resolutions(self, ids: list[str], texts: list[str], metadatas: list[dict]):
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

    def retrieve(self, query: str, k: int = None) -> list[dict]:
        k = k or settings.retrieval_k
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        return results
