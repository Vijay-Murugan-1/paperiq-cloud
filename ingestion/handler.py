import json
import urllib.parse
import boto3

from shared.embedding_generator import generate_embeddings
from shared.pdf_processor import extract_text_from_pdf
from shared.text_chunker import create_chunks
from shared.vector_store import upload_embeddings

s3_client = boto3.client("s3")

def lambda_handler(event, context):
    try:
        record = event["Records"][0]

        bucket_name = record["s3"]["bucket"]["name"]
        object_key = urllib.parse.unquote_plus(
            record["s3"]["object"]["key"]
        )

        if not object_key.lower().endswith(".pdf"):
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Uploaded file is not a PDF."}),
            }

        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=object_key,
        )

        pdf_bytes = response["Body"].read()

        # FIX: Set document_id directly to the object_key/filename
        document_id = object_key

        text = extract_text_from_pdf(pdf_bytes)
        chunks = create_chunks(text)
        embeddings = generate_embeddings(chunks)

        uploaded_count = upload_embeddings(
            document_id=document_id,
            filename=object_key,
            chunks=chunks,
            embeddings=embeddings,
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "PDF processed successfully.",
                    "document_id": document_id,
                    "filename": object_key,
                    "chunks_uploaded": uploaded_count,
                }
            ),
        }

    except Exception as error:
        print(f"Ingestion error: {error}")

        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "message": "PDF processing failed.",
                    "error": str(error),
                }
            ),
        }