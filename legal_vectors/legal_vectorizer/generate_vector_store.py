import os
import pymupdf4llm  # PyMuPDF
import google.generativeai as genai
from chromadb import Client
from chromadb.config import Settings
import chromadb
from typing import List
import re
from langchain.text_splitter import MarkdownTextSplitter

splitter = MarkdownTextSplitter(chunk_size=2048, chunk_overlap=300)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using pymupdf4llm"""
    try:
        doc = pymupdf4llm.to_markdown(pdf_path)
        return doc  # pymupdf4llm.to_markdown returns a string directly
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def get_gemini_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings using Google's Gemini embedding model
    """
    embeddings = []
    
    # Process texts in batches to avoid API limits
    batch_size = 100  # Adjust based on API limits
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=batch,
                task_type="retrieval_document",
                output_dimensionality=768
            )
            embeddings.extend(result['embedding'])
            print(f"✅ Generated embeddings for batch {i//batch_size + 1}")
            
        except Exception as e:
            print(f"❌ Error generating embeddings for batch {i//batch_size + 1}: {e}")
            # Add zero embeddings as fallback
            fallback_embedding = [0.0] * 768  # Default embedding dimension
            embeddings.extend([fallback_embedding] * len(batch))
    
    return embeddings

def generate_vector_store(data_folder: str = "../../data/selected_swiss_law"):

    """
    Generate vector store using Gemini embeddings
    """
    # Initialize persistent ChromaDB client and collection
    client = chromadb.PersistentClient(path="./chroma_db", settings=Settings())
    
    # Delete existing collection if it exists to avoid conflicts
    try:
        client.delete_collection(name="pdf_vectors_gemini")
    except:
        pass
    
    collection = client.create_collection(
        name="pdf_vectors_gemini",
        metadata={"description": "PDF vectors using Gemini embeddings"}
    )

    total_chunks = 0
    
    # Recursively traverse all subfolders
    for root, dirs, files in os.walk(data_folder):
        pdf_files = [f for f in files if f.lower().endswith(".pdf")]
        
        for filename in pdf_files:
            pdf_path = os.path.join(root, filename)
            print(f"📄 Processing: {pdf_path}")

            # Extract and chunk text
            text = extract_text_from_pdf(pdf_path)
            if not text:
                print(f"⚠️  No text extracted from {pdf_path}")
                continue
                
            chunks = [doc for doc in splitter.split_text(text)]
            print(f"📝 Created {len(chunks)} chunks from {filename}")

            if not chunks:
                print(f"⚠️  No chunks created from {pdf_path}")
                continue

            # Generate embeddings using Gemini
            embeddings = get_gemini_embeddings(chunks)

            # Add each chunk + its embedding to ChromaDB
            doc_ids = []
            documents = []
            metadatas = []
            embeddings_list = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                doc_id = f"{os.path.relpath(pdf_path, data_folder)}_{i}"
                doc_ids.append(doc_id)
                documents.append(chunk)
                embeddings_list.append(embedding)
                metadatas.append({
                    "source": pdf_path,
                    "chunk_index": i,
                    "filename": filename,
                    "chunk_size": len(chunk)
                })
            
            # Batch add to ChromaDB
            collection.add(
                documents=documents,
                embeddings=embeddings_list,
                ids=doc_ids,
                metadatas=metadatas
            )
            
            total_chunks += len(chunks)
            print(f"✅ Added {len(chunks)} chunks from {filename}")
    
    print(f"🎉 Total chunks processed: {total_chunks}")
    return collection

def query_gemini_embedding(query_text: str, model_name: str = "gemini-embedding-001") -> List[float]:
    """
    Generate embedding for query using Gemini
    """
    try:
        
        client = genai.Client()

        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=query_text
        )
        return [embedding.values for embedding in result.embeddings][0]
    except Exception as e:
        print(f"❌ Error generating query embedding: {e}")
        return [0.0] * 768  # Fallback

def query(collection, query_text: str = None, n_results: int = 3):
    """
    Query the vector database using Gemini embeddings
    """
    if query_text is None:
        query_text = "Does Swiss law require an employer to give multiple warnings before firing an employee for just cause?"
    
    print(f"\n🔍 Generating embedding for query: \"{query_text}\"\n")
    query_embedding = query_gemini_embedding(query_text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    print(f"📊 Found {len(results['documents'][0])} results:\n")

    for i in range(len(results["documents"][0])):
        doc = results["documents"][0][i]
        metadata = results["metadatas"][0][i] if results["metadatas"][0] else {}
        distance = results["distances"][0][i]
        
        print(f"📄 Result {i+1}")
        print(f"📁 Source: {metadata.get('filename', 'Unknown')}")
        print(f"🔢 Similarity Score: {1 - distance:.4f}")
        print(f"📏 Distance: {distance:.4f}")
        print(f"📝 Content Preview:\n{doc[:300]}...")
        print("-" * 80)

def main():
    """
    Main function to run the vectorization and query process
    """
    # Check if API key is set
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ Please set your GOOGLE_API_KEY environment variable")
        print("   export GOOGLE_API_KEY='your_api_key_here'")
        return
    
    print("🚀 Starting PDF vectorization with Gemini embeddings...")
    
    # Generate vector store
    collection = generate_vector_store()
    
    # Query the collection
    query(collection)
    
    # Interactive query mode
    print("\n" + "="*50)
    print("💬 Interactive Query Mode (type 'quit' to exit)")
    print("="*50)
    
    while True:
        user_query = input("\n🔍 Enter your query: ").strip()
        if user_query.lower() in ['quit', 'exit', 'q']:
            break
        if user_query:
            query(collection, user_query)

if __name__ == "__main__":
    main()