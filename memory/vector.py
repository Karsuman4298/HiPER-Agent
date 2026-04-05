from qdrant_client import QdrantClient
from qdrant_client.http import models
from config.settings import settings
import uuid
from typing import List, Dict, Any

class VectorMemory:
    def __init__(self, path: str = settings.QDRANT_PATH):
        self.client = QdrantClient(path=path)
        self.collection_name = "hyper_memory"
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )

    def add_memory(self, text: str, metadata: Dict[str, Any] = None):
        # In a real app, I'd use an embedding model here. 
        # For simplicity in this starter, I'll assume embeddings are handled externally or use a placeholder.
        # Actually, let's use a simple sentence-transformer if available or mock it.
        # For now, I'll implement the structure.
        point_id = str(uuid.uuid4())
        # Placeholder for embedding - in production, call Ollama or a local model
        dummy_vector = [0.0] * 384 
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=dummy_vector,
                    payload={"text": text, **(metadata or {})}
                )
            ]
        )

    def search_memory(self, query_text: str, limit: int = 5) -> List[Dict]:
        dummy_vector = [0.0] * 384
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=dummy_vector,
            limit=limit
        )
        return [hit.payload for hit in search_result]
