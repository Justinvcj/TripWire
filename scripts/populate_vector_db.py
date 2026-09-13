import json
import chromadb
from chromadb.utils import embedding_functions

print("Loading historical pairs...")
with open("data/historical_pairs.json", "r", encoding="utf-8") as f:
    pairs = json.load(f)

print("Initializing ChromaDB...")
client = chromadb.PersistentClient(path="./data/chroma")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

try:
    client.delete_collection("historical_resolutions")
    print("Deleted old collection.")
except:
    pass

collection = client.create_collection("historical_resolutions", embedding_function=embedding_fn)

ids = [p['tweet_id'] for p in pairs]
texts = [p['customer_text'] for p in pairs]
metadatas = [{"reference_reply": p['gold_reference_reply']} for p in pairs]

print(f"Adding {len(pairs)} records to Vector DB. This will take a moment...")
batch_size = 500
for i in range(0, len(pairs), batch_size):
    print(f"Batch {i}/{len(pairs)}")
    collection.add(
        ids=ids[i:i+batch_size],
        documents=texts[i:i+batch_size],
        metadatas=metadatas[i:i+batch_size]
    )

print("ChromaDB populated with real AmazonHelp resolutions!")
