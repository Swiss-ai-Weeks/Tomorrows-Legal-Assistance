import os
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from typing import List, Dict, Optional

class LegalRetriever:
    """
    A class to retrieve legal information from a ChromaDB vector store
    using Gemini embeddings for semantic search.
    """

    def __init__(self, collection_name: str = "pdf_vectors_gemini"):
        """
        Initialize the retriever and connect to the ChromaDB vector store.

        Args:
            collection_name (str): The name of the collection to query.
        """
        # --- Configuration ---
        # Use the chroma_db directory relative to this file's location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, "chroma_db")
        self.collection_name = collection_name
        
        # --- Configure Gemini API ---
        # Ensure the Google API Key is set in the environment variables.
        if not os.environ.get("GOOGLE_API_KEY"):
            raise ValueError("Please set the GOOGLE_API_KEY environment variable.")
        
        # --- Initialize ChromaDB Client ---
        try:
            # Create a persistent client that stores data on disk.
            self.client = chromadb.PersistentClient(path=self.db_path, settings=Settings())
            # Get the specified collection from the database.
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"✅ Successfully connected to collection '{self.collection_name}'.")
            print(f"📊 Collection contains {self.collection.count()} documents.")
        except Exception as e:
            # Raise a connection error if the database connection fails.
            raise ConnectionError(f"Failed to connect to ChromaDB at '{self.db_path}': {e}")
        
        self.client = genai.Client()

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate a vector embedding for the given text using the Gemini API.

        Args:
            text (str): The input text to embed.
            model (str): The name of the embedding model to use.

        Returns:
            List[float]: The generated vector embedding.
        """
        try:

            result = self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=text
            )
            return [embedding.values for embedding in result.embeddings][0]
        except Exception as e:
            print(f"❌ Error generating embedding for query: {e}")
            # Return a zero vector as a fallback.
            return [0.0] * 768

    def _search_vector_store(self, query: str, n_results: int = 3) -> Optional[Dict]:
        """
        Perform a semantic search in the ChromaDB collection.

        Args:
            query (str): The search query string.
            n_results (int): The number of top results to return.

        Returns:
            Optional[Dict]: A dictionary containing search results, or None if an error occurs.
        """
        # Generate an embedding for the user's query.
        query_embedding = self._generate_embedding(query)
        if not any(query_embedding): # Check if the embedding is just a zero vector
             return None

        # Query the collection for the most similar documents.
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        return results

    def retrieve(self, input: str, n_results: int = 3) -> dict:

        """
        Retrieve relevant document contents based on a query string.

        This method performs a semantic search and concatenates the content
        of the top matching documents into a single string.

        Args:
            input (str): The user's query or question.

        Returns:
            str: A string containing the combined content of the most
                 relevant documents, or a message if no results are found.
        """
        print(f"🔍 Retrieving documents for query: '{input}'")
        search_results = self._search_vector_store(input, n_results)
        return search_results
    
    
    def retrieve_str(self, input: str, n_results: int = 3) -> str:
        """
        Retrieve relevant document contents based on a query string.

        This method performs a semantic search and concatenates the content
        of the top matching documents into a single string.

        Args:
            input (str): The user's query or question.

        Returns:
            str: A string containing the combined content of the most
                 relevant documents, or a message if no results are found.
        """
        print(f"🔍 Retrieving documents for query: '{input}'")
        search_results = self._search_vector_store(input, n_results)
        if not search_results or not search_results.get("documents") or not search_results["documents"][0]:
            return "No relevant documents were found for your query."

        # Combine the text content of the retrieved documents.
        retrieved_docs = search_results["documents"][0]
        
        # Format the output with separators for clarity.
        formatted_output = []
        for i, doc in enumerate(retrieved_docs, 1):
            source = search_results["metadatas"][0][i-1].get('filename', 'Unknown Source')
            formatted_output.append(f"--- Retrieved Document [{i}] | Source: {source} ---\n\n{doc}")

        return "\n\n".join(formatted_output)

# Example of how to use the LegalRetriever class
if __name__ == '__main__':
    try:
        # NOTE: Make sure your GOOGLE_API_KEY is set as an environment variable
        # For example, in your terminal: export GOOGLE_API_KEY="your_api_key_here"
        
        print("Initializing LegalRetriever...")
        retriever = LegalRetriever()
        
        # Example query
        user_query = "What are the key responsibilities of a data protection officer under GDPR?"
        
        # Retrieve the information
        response = retriever.retrieve(user_query)
        
        # Print the results
        print("\n" + "="*80)
        print("RETRIEVED INFORMATION:")
        print("="*80)
        print(response)
        print("\n" + "="*80)

    except (ValueError, ConnectionError) as e:
        print(f"\nAn error occurred during initialization: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
