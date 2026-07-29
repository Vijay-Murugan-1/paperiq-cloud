# 📄 PaperIQ

PaperIQ is a serverless Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask questions, generate summaries, and extract key insights using AI. 

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **Backend:** AWS Lambda, Amazon API Gateway, Amazon S3
* **AI & Vector DB:** Google Gemini API (`gemini-2.5-flash`), Pinecone Vector Database
* **Infrastructure as Code:** AWS SAM

## 📁 Project Structure
* `/ingestion` - AWS Lambda code for processing and embedding PDFs from S3.
* `/assistant` - AWS Lambda code for the query API and LLM interaction.
* `/shared` - Shared utilities across Lambda functions.
* `template.yaml` - AWS SAM infrastructure template.

