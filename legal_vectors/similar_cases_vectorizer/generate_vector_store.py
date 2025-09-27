import os
from google import genai
from chromadb.config import Settings
import chromadb
from typing import List
from tqdm import tqdm


def get_gemini_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings using Google's Gemini embedding model
    """
    embeddings = []

    # Process texts in batches to avoid API limits
    batch_size = 100  # Adjust based on API limits

    for i in tqdm(range(0, len(texts), batch_size)):
        batch = texts[i : i + batch_size]
        try:
            # Generate embeddings for the batch
            client = genai.Client()

            result = client.models.embed_content(
                model="gemini-embedding-001", contents=batch
            )

            embeddings.extend([embedding.values for embedding in result.embeddings])
            # print(f"✅ Generated embeddings for batch {i//batch_size + 1}")

        except Exception as e:
            print(
                f"❌ Error generating embeddings for batch {i // batch_size + 1}: {e}"
            )
            # Add zero embeddings as fallback
            fallback_embedding = [0.0] * 768  # Default embedding dimension
            embeddings.extend([fallback_embedding] * len(batch))

    return embeddings


def generate_vector_store(
    data_folder: str = "../../data/emails_federal_court/*.parquet",
    path_base_df: str = "../../data/bger-2024-3.csv",
):
    """
    Generate vector store using Gemini embeddings
    """
    # Initialize persistent ChromaDB client and collection
    client = chromadb.PersistentClient(path="./chroma_db", settings=Settings())

    import pandas as pd
    import glob

    files = glob.glob(data_folder)
    df_emails = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

    df_base = pd.read_csv(path_base_df)

    df = pd.merge(df_base, df_emails, on="docref", how="inner")

    # Drop rows where the 'email' column is empty
    df.dropna(subset=["email"], inplace=True)

    import pandas as pd

    # First, find the number of samples in the smallest class
    min_count = df["outcome"].value_counts().min()

    # Now, group by the 'outcomes' column and take a random sample of 'min_count' from each group
    df_balanced = df.groupby("outcome").sample(n=min_count, random_state=42)

    # It's good practice to shuffle the resulting dataframe
    df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

    # Now, df_balanced has a 50/50 split
    # print(df_balanced['case_status'].value_counts())

    df_balanced = df_balanced.sample(frac=0.1, random_state=42)

    # Delete existing collection if it exists to avoid conflicts
    try:
        client.delete_collection(name="similar_vectors_gemini")
    except:
        pass

    collection = client.create_collection(
        name="similar_vectors_gemini",
        metadata={
            "description": "emails similar cases vectors using Gemini embeddings"
        },
    )

    # TODO: Prepare emails from the 'email' column
    emails_prepared = df_balanced["email"].astype(str).tolist()

    embeddings = get_gemini_embeddings(emails_prepared)

    doc_ids = []
    documents = []
    metadatas = []
    embeddings_list = []

    for i, (chunk, embedding) in enumerate(zip(emails_prepared, embeddings)):
        # TODO: Create unique document ID
        doc_id = f"email_{i}_{hash(chunk) % 1000000}"
        doc_ids.append(doc_id)
        documents.append(chunk)
        embeddings_list.append(embedding)

        # TODO: Create metadata from all other columns
        row_metadata = {}
        for col in df_balanced.columns:
            if (
                col != "email"
            ):  # Exclude the email column since it's the document content
                value = df_balanced.iloc[i][col]
                # Convert to string and handle NaN values
                if pd.isna(value):
                    row_metadata[col] = ""
                else:
                    row_metadata[col] = str(value)

        metadatas.append(row_metadata)

    # Batch add to ChromaDB
    collection.add(
        documents=documents,
        embeddings=embeddings_list,
        ids=doc_ids,
        metadatas=metadatas,
    )

    print(f"✅ Added {len(df_balanced)} chunks from {path_base_df}")

    print(f"🎉 Total chunks processed: {len(df_balanced)}")

    return collection


def query_gemini_embedding(
    query_text: str, model_name: str = "gemini-embedding-001"
) -> List[float]:
    """
    Generate embedding for query using Gemini
    """
    try:
        client = genai.Client()

        result = client.models.embed_content(
            model="gemini-embedding-001", contents=query_text
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

    print(f'\n🔍 Generating embedding for query: "{query_text}"\n')
    query_embedding = query_gemini_embedding(query_text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    print(f"📊 Found {len(results['documents'][0])} results:\n")

    for i in range(len(results["documents"][0])):
        doc = results["documents"][0][i]
        metadata = results["metadatas"][0][i] if results["metadatas"][0] else {}
        distance = results["distances"][0][i]

        print(f"📄 Result {i + 1}")
        print(f"📁 Source: {metadata.get('filename', 'Unknown')}")
        print(f"🔢 Similarity Score: {1 - distance:.4f}")
        print(f"📏 Distance: {distance:.4f}")
        print(f"📝 Content Preview:\n{doc[:300]}...")

        # Display some metadata fields
        print("📋 Metadata:")
        for key, value in list(metadata.items())[:5]:  # Show first 5 metadata fields
            if key != "filename":  # Already shown above
                print(f"   {key}: {value}")
        if len(metadata) > 5:
            print(f"   ... and {len(metadata) - 5} more fields")

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

    print("🚀 Starting df vectorization with Gemini embeddings...")

    # Generate vector store
    collection = generate_vector_store()

    # Query the collection
    query(collection)

    # Interactive query mode
    print("\n" + "=" * 50)
    print("💬 Interactive Query Mode (type 'quit' to exit)")
    print("=" * 50)

    while True:
        user_query = input("\n🔍 Enter your query: ").strip()
        if user_query.lower() in ["quit", "exit", "q"]:
            break
        if user_query:
            query(collection, user_query)


if __name__ == "__main__":
    main()
