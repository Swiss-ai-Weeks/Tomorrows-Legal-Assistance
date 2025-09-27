import os
from google import genai
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Union
import pandas as pd
from dataclasses import dataclass, asdict
import json


@dataclass
class RetrievalResult:
    """
    Structured result object for retrieval operations
    """
    id: str
    document: str
    metadata: Dict[str, Any]
    distance: float
    similarity_score: float
    rank: int


@dataclass
class RetrievalResponse:
    """
    Complete response object containing all retrieval information
    """
    query: str
    query_embedding: List[float]
    results: List[RetrievalResult]
    total_results: int
    execution_time: float
    collection_info: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return asdict(self)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to pandas DataFrame"""
        data = []
        for result in self.results:
            row = {
                'id': result.id,
                'document': result.document,
                'distance': result.distance,
                'similarity_score': result.similarity_score,
                'rank': result.rank
            }
            # Add metadata fields as separate columns
            row.update(result.metadata)
            data.append(row)
        return pd.DataFrame(data)


class OptimizedChromaRetriever:
    """
    Optimized retrieval class for ChromaDB with Gemini embeddings
    """
    
    def __init__(self, 
                 chroma_db_path: str = "./chroma_db", 
                 collection_name: str = "similar_vectors_gemini",
                 embedding_model: str = "gemini-embedding-001"):
        """
        Initialize the retriever
        
        Args:
            chroma_db_path: Path to ChromaDB storage
            collection_name: Name of the collection to query
            embedding_model: Gemini embedding model to use
        """
        self.chroma_db_path = chroma_db_path
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.client = None
        self.collection = None
        self.genai_client = None
        
        # Initialize connections
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize ChromaDB and Gemini API connections"""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.chroma_db_path, 
                settings=Settings()
            )
            
            # Get collection
            self.collection = self.client.get_collection(name=self.collection_name)
            
            # Initialize Gemini client
            self.genai_client = genai.Client()
            
            print(f"✅ Connected to ChromaDB collection: {self.collection_name}")
            print(f"📊 Collection count: {self.collection.count()}")
            
        except Exception as e:
            print(f"❌ Error initializing connections: {e}")
            raise
    
    def _generate_query_embedding(self, query_text: str) -> List[float]:
        """
        Generate embedding for query text using Gemini
        
        Args:
            query_text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            result = self.genai_client.models.embed_content(
                model=self.embedding_model,
                contents=query_text
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"❌ Error generating query embedding: {e}")
            return [0.0] * 768  # Fallback embedding
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the collection
        
        Returns:
            Dictionary with collection statistics and metadata
        """
        try:
            count = self.collection.count()
            
            # Get a sample of documents to analyze metadata structure
            sample = self.collection.get(limit=5, include=["metadatas", "documents"])
            
            # Analyze metadata fields
            metadata_fields = set()
            if sample['metadatas']:
                for metadata in sample['metadatas']:
                    if metadata:
                        metadata_fields.update(metadata.keys())
            
            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "metadata_fields": list(metadata_fields),
                "sample_document_length": len(sample['documents'][0]) if sample['documents'] else 0,
                "embedding_model": self.embedding_model
            }
        except Exception as e:
            print(f"❌ Error getting collection info: {e}")
            return {}
    
    def retrieve(self, 
                 query_text: str,
                 n_results: int = 10,
                 where_filter: Optional[Dict[str, Any]] = None,
                 where_document_filter: Optional[Dict[str, str]] = None,
                 include_embedding: bool = False) -> RetrievalResponse:
        """
        Comprehensive retrieval method that returns all available information
        
        Args:
            query_text: Text query to search for
            n_results: Number of results to return
            where_filter: Metadata filtering conditions
            where_document_filter: Document content filtering conditions
            include_embedding: Whether to include query embedding in response
            
        Returns:
            RetrievalResponse object with complete information
        """
        import time
        start_time = time.time()
        
        try:
            # Generate query embedding
            query_embedding = self._generate_query_embedding(query_text)
            
            # Prepare query parameters
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": n_results,
                "include": ["documents", "metadatas", "distances"]
            }
            
            # Add filters if provided
            if where_filter:
                query_params["where"] = where_filter
            if where_document_filter:
                query_params["where_document"] = where_document_filter
            
            # Execute query
            results = self.collection.query(**query_params)
            
            # Process results
            processed_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    result = RetrievalResult(
                        id=results['ids'][0][i],
                        document=results['documents'][0][i],
                        metadata=results['metadatas'][0][i] if results['metadatas'][0][i] else {},
                        distance=results['distances'][0][i],
                        similarity_score=1 - results['distances'][0][i],
                        rank=i + 1
                    )
                    processed_results.append(result)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Get collection info
            collection_info = self.get_collection_info()
            
            # Create response object
            response = RetrievalResponse(
                query=query_text,
                query_embedding=query_embedding if include_embedding else [],
                results=processed_results,
                total_results=len(processed_results),
                execution_time=execution_time,
                collection_info=collection_info
            )
            
            return response
            
        except Exception as e:
            print(f"❌ Error during retrieval: {e}")
            return RetrievalResponse(
                query=query_text,
                query_embedding=[],
                results=[],
                total_results=0,
                execution_time=time.time() - start_time,
                collection_info=self.get_collection_info()
            )
    
    def retrieve_by_metadata(self, 
                           metadata_filter: Dict[str, Any],
                           n_results: int = 10) -> List[RetrievalResult]:
        """
        Retrieve documents based on metadata filtering only (no semantic search)
        
        Args:
            metadata_filter: Metadata conditions to filter by
            n_results: Maximum number of results
            
        Returns:
            List of RetrievalResult objects
        """
        try:
            results = self.collection.get(
                where=metadata_filter,
                limit=n_results,
                include=["documents", "metadatas"]
            )
            
            processed_results = []
            if results['documents']:
                for i in range(len(results['documents'])):
                    result = RetrievalResult(
                        id=results['ids'][i],
                        document=results['documents'][i],
                        metadata=results['metadatas'][i] if results['metadatas'][i] else {},
                        distance=0.0,  # No distance for metadata-only search
                        similarity_score=1.0,  # Perfect match for metadata filtering
                        rank=i + 1
                    )
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            print(f"❌ Error during metadata retrieval: {e}")
            return []
    
    def retrieve_by_ids(self, document_ids: List[str]) -> List[RetrievalResult]:
        """
        Retrieve specific documents by their IDs
        
        Args:
            document_ids: List of document IDs to retrieve
            
        Returns:
            List of RetrievalResult objects
        """
        try:
            results = self.collection.get(
                ids=document_ids,
                include=["documents", "metadatas"]
            )
            
            processed_results = []
            if results['documents']:
                for i in range(len(results['documents'])):
                    result = RetrievalResult(
                        id=results['ids'][i],
                        document=results['documents'][i],
                        metadata=results['metadatas'][i] if results['metadatas'][i] else {},
                        distance=0.0,
                        similarity_score=1.0,
                        rank=i + 1
                    )
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            print(f"❌ Error during ID-based retrieval: {e}")
            return []
    
    def get_similar_documents(self, 
                            document_id: str, 
                            n_results: int = 5) -> RetrievalResponse:
        """
        Find documents similar to a specific document in the collection
        
        Args:
            document_id: ID of the reference document
            n_results: Number of similar documents to return
            
        Returns:
            RetrievalResponse with similar documents
        """
        try:
            # First get the reference document
            ref_doc = self.collection.get(
                ids=[document_id],
                include=["documents", "embeddings"]
            )
            
            if not ref_doc['documents']:
                raise ValueError(f"Document with ID {document_id} not found")
            
            # Use its embedding to find similar documents
            ref_embedding = ref_doc['embeddings'][0] if ref_doc['embeddings'] else None
            
            if ref_embedding:
                results = self.collection.query(
                    query_embeddings=[ref_embedding],
                    n_results=n_results + 1,  # +1 to account for the reference document itself
                    include=["documents", "metadatas", "distances"]
                )
                
                # Remove the reference document from results
                processed_results = []
                for i in range(len(results['documents'][0])):
                    if results['ids'][0][i] != document_id:
                        result = RetrievalResult(
                            id=results['ids'][0][i],
                            document=results['documents'][0][i],
                            metadata=results['metadatas'][0][i] if results['metadatas'][0][i] else {},
                            distance=results['distances'][0][i],
                            similarity_score=1 - results['distances'][0][i],
                            rank=len(processed_results) + 1
                        )
                        processed_results.append(result)
                        
                        if len(processed_results) >= n_results:
                            break
                
                return RetrievalResponse(
                    query=f"Similar to document: {document_id}",
                    query_embedding=[],
                    results=processed_results,
                    total_results=len(processed_results),
                    execution_time=0.0,
                    collection_info=self.get_collection_info()
                )
            else:
                raise ValueError("No embedding found for reference document")
                
        except Exception as e:
            print(f"❌ Error finding similar documents: {e}")
            return RetrievalResponse(
                query=f"Similar to document: {document_id}",
                query_embedding=[],
                results=[],
                total_results=0,
                execution_time=0.0,
                collection_info=self.get_collection_info()
            )
    
    def export_results(self, 
                      response: RetrievalResponse, 
                      format_type: str = "json",
                      filename: Optional[str] = None) -> str:
        """
        Export retrieval results to file
        
        Args:
            response: RetrievalResponse object to export
            format_type: Export format ("json", "csv", "excel")
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        import datetime
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"retrieval_results_{timestamp}"
        
        try:
            if format_type.lower() == "json":
                filepath = f"{filename}.json"
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(response.to_dict(), f, indent=2, ensure_ascii=False)
                    
            elif format_type.lower() == "csv":
                filepath = f"{filename}.csv"
                df = response.to_dataframe()
                df.to_csv(filepath, index=False, encoding='utf-8')
                
            elif format_type.lower() == "excel":
                filepath = f"{filename}.xlsx"
                df = response.to_dataframe()
                df.to_excel(filepath, index=False, engine='openpyxl')
                
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            print(f"✅ Results exported to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error exporting results: {e}")
            return ""


# Example usage and testing functions
def example_usage():
    """
    Example of how to use the OptimizedChromaRetriever
    """
    # Check API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ Please set your GOOGLE_API_KEY environment variable")
        return
    
    # Initialize retriever
    retriever = OptimizedChromaRetriever()
    
    # Example 1: Basic semantic search
    print("\n🔍 Example 1: Basic Semantic Search")
    response = retriever.retrieve(
        query_text="employment law termination procedures",
        n_results=5
    )
    
    print(f"Query: {response.query}")
    print(f"Found {response.total_results} results in {response.execution_time:.3f}s")
    
    for result in response.results[:2]:  # Show first 2 results
        print(f"\n📄 Rank {result.rank} (Score: {result.similarity_score:.4f})")
        print(f"ID: {result.id}")
        print(f"Content: {result.document[:200]}...")
        print(f"Metadata keys: {list(result.metadata.keys())}")
    
    # Example 2: Filtered search
    print("\n🎯 Example 2: Filtered Search")
    # Assuming you have a 'category' or similar field in metadata
    filtered_response = retriever.retrieve(
        query_text="contract disputes",
        n_results=3,
        where_filter={"docref": {"$ne": ""}}  # Non-empty docref
    )
    
    print(f"Filtered results: {filtered_response.total_results}")
    
    # Example 3: Export results
    print("\n💾 Example 3: Export Results")
    filepath = retriever.export_results(response, format_type="json")
    print(f"Exported to: {filepath}")
    
    # Example 4: Convert to DataFrame for analysis
    print("\n📊 Example 4: DataFrame Conversion")
    df = response.to_dataframe()
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")


if __name__ == "__main__":
    example_usage()