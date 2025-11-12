import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid

class ConversationMemory:
    def __init__(self, limit: int = 10):
        self.client = chromadb.PersistentClient(path="backend/data/vector_db/short_term")
        self.collection = self.client.get_or_create_collection(name="conversation_memory")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.limit = limit

    def add_message(self, role: str, text: str):
        timestamp = datetime.now().isoformat()
        embedding = self.model.encode([text])[0]
        id = str(uuid.uuid4())
        
        self.collection.add(
            ids=[id],
            documents=[text],
            embeddings=[embedding.tolist()],
            metadatas=[{"role": role, "timestamp": timestamp}]
        )
        self._enforce_limit()

    def _enforce_limit(self):
        results = self.collection.get(include=["metadatas", "documents"])
        docs = results.get("documents", [])
        ids = results.get("ids", [])
        if len(docs) > self.limit:
            to_delete = ids[:-self.limit]
            self.collection.delete(ids=to_delete)

    def retrieve_relevant(self, query: str, top_k: int = 2):
        embedding = self.model.encode([query])[0]
        results = self.collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=top_k
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        return list(zip(docs, metas))
    
    def retrieve_all(self):
        results = self.collection.get(
            include=["documents","metadatas"]
        )
        docs = results.get("documents",[])
        metadata = results.get("metadatas",[])
        
        combined = list(zip(docs, metadata))
        return combined[::-1]
