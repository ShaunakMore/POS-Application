import chromadb
from sentence_transformers import SentenceTransformer
import uuid

class VectorMemory:
  def __init__(self, file_path="backend/data/memory_store.json"):
    self.client = chromadb.PersistentClient(path="backend/data/vector_db")
    self.collection = self.client.get_or_create_collection(name="pos_memory")
    self.model = SentenceTransformer("all-MiniLM-L6-v2") 
  
  def add_memory(self, text:str, mem_type:str="conversation"):
    """
    Adds memory with its embedding to ChromaDB
    """
    embedding = self.model.encode([text])[0]
    mem_id = str(uuid.uuid4())
    
    self.collection.add(
      ids=[mem_id],
      documents=[text],
      embeddings=[embedding.tolist()],
      metadatas=[{"type":mem_type}]
    )
  
  def search_memory(self, query, k=3):
    """
    Retrieves symantically similar memories
    """
    embedding = self.model.encode([query])[0]
    results = self.collection.query(
      query_embeddings=[embedding.tolist()],
      n_results = k
    )
    docs = results.get("documents",[[]])[0]
    metas = results.get("metadatas",[[]])[0]
    
    return list(zip(docs,metas))
  
  def get_all_memories(self,limit:int=5):
    results = self.collection.get(
      include=["documents","metadatas"]
    )
    docs = results.get("documents",[])
    metadata = results.get("metadatas",[])
    
    combined = list(zip(docs, metadata))[-limit:]
    return combined[::-1]