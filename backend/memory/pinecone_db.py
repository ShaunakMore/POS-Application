from pinecone import Pinecone
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

index_name = "memory"
pc = Pinecone(os.getenv("PINECONE_API_KEY"))

index = pc.Index(index_name)

def add_memory(text:str,mem_type:str="conversational"):
  """
    Adds memory to Pinecone
  """
  id = str(uuid.uuid4())
  
  record = {
    "id":id,
    "text": text,
    "type": mem_type
  }
  try:
    index.upsert_records("long_term",[record])
    print("\nLong term Memory added to PineconeDB ✅")
  except Exception as e:
    print(f"Could not add long term memory to PineconeDB ⚠️: {e}")

def search_memory(query:str, k=3):
  
  try:
    results = index.search(
      namespace="long_term",
      query={
          "top_k": k,
          "inputs": {
              'text': query
          }
      }
  )
    print(results)
    data = [hit['fields']['text'] for hit in results['result']['hits']]
    category = [hit['fields']['type'] for hit in results['result']['hits']]
    
    print("Long term memory query successfull on pinecone ✅")
    return list(zip(data,category))
  except Exception as e:
    print(f"Could'nt query pinecone: {e}")
    
def add_previous_convos(convo:str):
  """
  Add short term memory to Pinecone
  """
  id = str(uuid.uuid4())
  
  record = {
    "id":id,
    "text": convo,
  }
  try:
    index.delete(namespace="short_term",delete_all=True)
    index.upsert_records("short_term",[record])
    print("\nShort Term Memory added to PineconeDB ✅")
  except Exception as e:
    print(f"Could not add short term memory to PineconeDB ⚠️: {e}")
    
def get_all_long_term_mems(num=5):
  
  list_paginator = index.list(namespace="long_term", limit=num)

  all_ids = []
  try:
      all_ids = next(list_paginator) 
  except StopIteration:
      print("Namespace 'long_term' is empty.")

  vectors = None
  if all_ids:
      vectors = list(index.fetch(ids=all_ids, namespace="long_term").vectors.values())
      mems = [vec.metadata["text"] for vec in vectors]
      return mems