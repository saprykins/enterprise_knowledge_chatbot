from celery import shared_task
from django.utils import timezone
import logging

from .models import DataSource
from .rag_service import RAGService

logger = logging.getLogger(__name__)


@shared_task
def process_document_task(data_source_id: str):
    """Celery task to process a document asynchronously."""
    try:
        # Get the data source
        data_source = DataSource.objects.get(id=data_source_id)
        
        # Initialize RAG service
        rag_service = RAGService()
        
        # Process the document
        success = rag_service.process_document(data_source)
        
        if success:
            logger.info(f"Successfully processed document: {data_source.name}")
        else:
            logger.error(f"Failed to process document: {data_source.name}")
            
        return success
        
    except DataSource.DoesNotExist:
        logger.error(f"Data source {data_source_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error processing document {data_source_id}: {str(e)}")
        return False


@shared_task
def delete_document_chunks_task(data_source_id: str):
    """Celery task to delete document chunks asynchronously."""
    try:
        # Get the data source
        data_source = DataSource.objects.get(id=data_source_id)
        
        # Initialize RAG service
        rag_service = RAGService()
        
        # Delete chunks
        success = rag_service.delete_document_chunks(data_source)
        
        if success:
            logger.info(f"Successfully deleted chunks for: {data_source.name}")
        else:
            logger.error(f"Failed to delete chunks for: {data_source.name}")
            
        return success
        
    except DataSource.DoesNotExist:
        logger.error(f"Data source {data_source_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error deleting chunks for {data_source_id}: {str(e)}")
        return False


@shared_task
def cleanup_failed_documents_task():
    """Celery task to cleanup failed document processing."""
    try:
        # Find documents that have been in 'processing' status for too long
        cutoff_time = timezone.now() - timezone.timedelta(hours=1)
        failed_docs = DataSource.objects.filter(
            status='processing',
            processing_started_at__lt=cutoff_time
        )
        
        for doc in failed_docs:
            doc.status = 'failed'
            doc.error_message = 'Processing timed out'
            doc.save()
            logger.info(f"Marked {doc.name} as failed due to timeout")
            
        return len(failed_docs)
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        return 0
