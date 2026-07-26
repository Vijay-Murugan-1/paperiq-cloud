import os
import json
import logging
import boto3
import tempfile

from urllib.parse import unquote_plus
from shared.pdf_processor import process_pdf
from shared.text_chunker import create_chunks
from shared.embedding_generator import generate_embeddings
from shared.vector_store import upload_embeddings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")

def lambda_handler(event, context):
    """
    S3 trigger handler to process PDF and upload embeddings to Pinecone.
    """
    logger.info("Received event: %s", json.dumps(event))
    
    try:
        # Loop through each record in the S3 event
        for record in event.get("Records", []):
            bucket_name = record["s3"]["bucket"]["name"]
            object_key = unquote_plus(record["s3"]["object"]["key"])
            
            logger.info("Processing file %s from bucket %s", object_key, bucket_name)
            
            if not object_key.lower().endswith(".pdf"):
                logger.warning("Skipping non-PDF file: %s", object_key)
                continue
            
            download_path = os.path.join(tempfile.gettempdir(), os.path.basename(object_key))
            
            # Download PDF from S3
            logger.info("Downloading file to %s", download_path)
            s3_client.download_file(bucket_name, object_key, download_path)
            
            # Process PDF to extract page-numbered text blocks
            logger.info("Extracting text from PDF...")
            blocks = process_pdf(download_path)
            
            document_id = os.path.splitext(os.path.basename(object_key))[0]
            
            total_chunks = 0
            
            for block in blocks:
                page_text = block["text"]
                # Chunk the text
                chunks = create_chunks(page_text)
                
                if not chunks:
                    continue
                
                # Generate embeddings for the chunks
                embeddings = generate_embeddings(chunks)
                
                # Upsert vectors to Pinecone
                uploaded_count = upload_embeddings(
                    document_id=document_id,
                    filename=object_key,
                    chunks=chunks,
                    embeddings=embeddings,
                    page_number=block['page_number']
                )
                total_chunks += uploaded_count
            
            logger.info("Successfully processed and upserted %d total chunks for file %s", total_chunks, object_key)
            
            # Clean up the temp file
            if os.path.exists(download_path):
                os.remove(download_path)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Successfully processed S3 event"})
        }

    except Exception as e:
        logger.error("Error processing S3 event: %s", str(e), exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error during processing"})
        }
