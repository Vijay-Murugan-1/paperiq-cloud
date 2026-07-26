import json
from dotenv import load_dotenv

# Load local .env variables
load_dotenv()

# Import your Lambda handler function
from assistant.handler import lambda_handler

# Mock API Gateway Event with correct parameter names
mock_event = {
    "body": json.dumps({
        "task": "qa",
        "document_id": "test_doc_123",
        "question": "What are the main findings in this document?"
    })
}

print("--- Running Direct Lambda Handler Test ---")
response = lambda_handler(mock_event, None)

print("\n--- Handler Response ---")
print(json.dumps(response, indent=2))