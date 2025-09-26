import os
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from chromadb import Client
from chromadb.config import Settings

model = SentenceTransformer("all-MiniLM-L6-v2")
import chromadb



def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def chunk_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def generate_vector_store(data_folder="data"):
    # Initialize persistent ChromaDB client and collection
    client = chromadb.PersistentClient(path="./chroma_db", settings=Settings())
    collection = client.get_or_create_collection(name="pdf_vectors")

    # Recursively traverse all subfolders
    for root, dirs, files in os.walk(data_folder):
        for filename in files:
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                print(f"📄 Processing: {pdf_path}")

                # Extract and chunk text
                text = extract_text_from_pdf(pdf_path)
                chunks = chunk_text(text)

                # Generate embeddings for all chunks at once
                embeddings = model.encode(chunks, show_progress_bar=True)

                # Add each chunk + its embedding to ChromaDB
                for i, chunk in enumerate(chunks):
                    doc_id = f"{os.path.relpath(pdf_path, data_folder)}_{i}"
                    collection.add(
                        documents=[chunk],
                        embeddings=[embeddings[i].tolist()],
                        ids=[doc_id]
                    )

    return collection
        


def query(collection):
    query_text = "Does Swiss law require an employer to give multiple warnings before firing an employee for just cause?"
    query_embedding = model.encode([query_text])

    results = collection.query(
    query_embeddings=query_embedding,
    n_results=1,
    include=["documents", "metadatas", "distances"]
    )

    print(f"\n🔍 Query results: \"{query_text}\"\n")

    for i in range(len(results["documents"][0])):
        doc = results["documents"][0][i]
        doc_id = results["metadatas"][0][i]
        distance = results["distances"][0][i]
    
        print(f"📄 Document {i+1} (ID: {doc_id})")
        print(f"🔢 Similarity: {1 - distance:.2f}")
        print(f"📝 text:\n{doc[:500]}...\n")  

if __name__ == "__main__":
    collection=generate_vector_store()
    query(collection)
