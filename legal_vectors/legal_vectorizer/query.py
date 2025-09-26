import sys
from datetime import datetime
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

def query(query_text, persist_dir="./chroma_db", collection_name="pdf_vectors", top_k=2):
    start_time = datetime.now()
    print(f"⏳ Query started at: {start_time}")

    # Load embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode([query_text])

    # Connect to ChromaDB (embedded)
    client = chromadb.PersistentClient(path="./chroma_db", settings=Settings())
    print(client.list_collections())
    collection = client.get_collection(name=collection_name)

    # Perform query
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents",  "distances"]
    )

    # Print results
    print(f"\n🔍 Results for Query: \"{query_text}\"\n")
    for i in range(len(results["documents"][0])):
        doc = results["documents"][0][i]
        distance = results["distances"][0][i]
        print(f"🔢 Similarity: {1 - distance:.2f}")
        print(f"📝 Estratto:\n{doc[:1000]}...\n")  

    end_time = datetime.now()
    print(f"✅ Query completed at: {end_time}")
    print(f"⏱️ Total execution time: {end_time - start_time}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Ex: poetry run python query.py 'in which country is this happening'")
    else:
        query_text = " ".join(sys.argv[1:])
        query(query_text)

