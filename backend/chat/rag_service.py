import os
import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from django.utils import timezone

import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from .models import DataSource, DocumentChunk
from .services import LLMService

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG (Retrieval-Augmented Generation) operations."""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection_name = "company_documents"
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
        except:
            self.collection = self.chroma_client.create_collection(self.collection_name)
        
        # Initialize vector store
        self.vector_store = Chroma(
            client=self.chroma_client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # RAG prompt template
        self.rag_prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            You are a helpful AI assistant with access to company knowledge. Use the following context to answer the user's question.
            
            Context:
            {context}
            
            Question: {question}
            
            Answer based on the context provided. If the context doesn't contain relevant information, say so but still try to be helpful.
            """
        )
    
    def process_document(self, data_source: DataSource) -> bool:
        """Process a document and add it to the vector database."""
        try:
            logger.info(f"Processing document: {data_source.name}")
            
            # Update status to processing
            data_source.status = 'processing'
            data_source.processing_started_at = timezone.now()
            data_source.save()
            
            # Load document based on type
            if data_source.source_type == 'pdf':
                documents = self._load_pdf(data_source.file_path.path)
            else:
                raise ValueError(f"Unsupported source type: {data_source.source_type}")
            
            if not documents:
                raise ValueError("No content found in document")
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Process chunks and add to database
            chunk_objects = []
            for i, chunk in enumerate(chunks):
                # Create embedding ID
                embedding_id = f"{data_source.id}_{i}"
                
                # Add to ChromaDB
                self.collection.add(
                    documents=[chunk.page_content],
                    metadatas=[{
                        'source': data_source.name,
                        'chunk_index': i,
                        'page_number': chunk.metadata.get('page', None),
                        'data_source_id': str(data_source.id)
                    }],
                    ids=[embedding_id]
                )
                
                # Create DocumentChunk object
                chunk_obj = DocumentChunk.objects.create(
                    data_source=data_source,
                    content=chunk.page_content,
                    chunk_index=i,
                    page_number=chunk.metadata.get('page', None),
                    embedding_id=embedding_id,
                    token_count=len(chunk.page_content.split()),
                    metadata=chunk.metadata
                )
                chunk_objects.append(chunk_obj)
            
            # Update data source
            data_source.status = 'completed'
            data_source.processing_completed_at = timezone.now()
            data_source.total_chunks = len(chunk_objects)
            data_source.total_tokens = sum(chunk.token_count for chunk in chunk_objects)
            data_source.save()
            
            logger.info(f"Successfully processed {len(chunk_objects)} chunks for {data_source.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing document {data_source.name}: {str(e)}")
            data_source.status = 'failed'
            data_source.error_message = str(e)
            data_source.save()
            return False
    
    def _load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF document using PyPDFLoader."""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            raise
    
    def retrieve_relevant_chunks(self, query: str, k: int = 5) -> List[DocumentChunk]:
        """Retrieve relevant document chunks for a query."""
        try:
            # Search in ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            
            # Get DocumentChunk objects
            chunk_ids = results['ids'][0]
            chunks = []
            for chunk_id in chunk_ids:
                try:
                    chunk = DocumentChunk.objects.get(embedding_id=chunk_id)
                    chunks.append(chunk)
                except DocumentChunk.DoesNotExist:
                    logger.warning(f"Chunk {chunk_id} not found in database")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            return []
    
    def generate_rag_response(self, query: str, conversation_id: int) -> str:
        """Generate a response using RAG."""
        try:
            start_time = time.time()
            
            # Retrieve relevant chunks
            chunks = self.retrieve_relevant_chunks(query)
            retrieval_time = time.time() - start_time
            
            if not chunks:
                return "I don't have access to relevant company documents for this query. Let me help you with general information instead."
            
            # Prepare context from chunks
            context = "\n\n".join([chunk.content for chunk in chunks])
            
            # Generate response using LLM
            generation_start = time.time()
            
            messages = [
                {'role': 'system', 'content': self.rag_prompt_template.format(
                    context=context,
                    question=query
                )},
                {'role': 'user', 'content': query}
            ]
            
            response = self.llm_service.generate_response(messages)
            generation_time = time.time() - generation_start
            
            # Store RAG query for analytics
            from .models import RAGQuery, Conversation
            conversation = Conversation.objects.get(id=conversation_id)
            
            rag_query = RAGQuery.objects.create(
                conversation=conversation,
                query=query,
                response=response,
                retrieval_time=retrieval_time,
                generation_time=generation_time,
                total_tokens_used=len(response.split())  # Approximate
            )
            rag_query.retrieved_chunks.set(chunks)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def get_active_sources(self) -> List[DataSource]:
        """Get all active data sources."""
        return DataSource.objects.filter(is_active=True, status='completed')
    
    def delete_document_chunks(self, data_source: DataSource) -> bool:
        """Delete all chunks for a data source."""
        try:
            # Delete from ChromaDB
            chunks = DocumentChunk.objects.filter(data_source=data_source)
            embedding_ids = [chunk.embedding_id for chunk in chunks]
            
            if embedding_ids:
                self.collection.delete(ids=embedding_ids)
            
            # Delete from database
            chunks.delete()
            
            # Reset data source stats
            data_source.total_chunks = 0
            data_source.total_tokens = 0
            data_source.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting chunks for {data_source.name}: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG database."""
        try:
            total_sources = DataSource.objects.count()
            active_sources = DataSource.objects.filter(is_active=True).count()
            total_chunks = DocumentChunk.objects.count()
            total_tokens = sum(chunk.token_count for chunk in DocumentChunk.objects.all())
            
            return {
                'total_sources': total_sources,
                'active_sources': active_sources,
                'total_chunks': total_chunks,
                'total_tokens': total_tokens,
                'collection_size': self.collection.count()
            }
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {}
