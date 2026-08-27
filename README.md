# PaperIQ 📚

> An AI-powered research assistant for academic papers built with a serverless AWS architecture, Pinecone vector search, Gemini AI, and Streamlit.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://paperiq-cloud.streamlit.app)
[![AWS Serverless](https://img.shields.io/badge/AWS-Serverless-orange.svg)](https://aws.amazon.com/serverless/)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)

---

## 🌟 Overview

**PaperIQ** helps researchers, students, and professionals quickly digest complex academic papers. By uploading a PDF, PaperIQ processes the document through an automated serverless cloud pipeline to enable dynamic vector search and generative AI outputs.

### Key Features

* 📄 **Instant PDF Ingestion:** Upload papers directly to Amazon S3 to automatically trigger background extraction and vectorization.
* 📝 **Summary Generation:** Get high-level executive summaries of complex research papers.
* 💬 **Retrieval-Augmented Generation (RAG) Q&A:** Ask natural language questions about the paper and receive precise context-backed answers.
* 💡 **Key Insights Extraction:** Extract core takeaways, methodologies, and findings formatted into clean visual callouts.
* 🧪 **Interactive Quiz Generator:** Test your comprehension with dynamically generated multiple-choice quizzes complete with answer keys and explanations.
* 🎴 **Interactive Flashcards:** Review key terminology, concepts, and formulas using interactive flip cards.

---

## 🏗️ Architecture & Cloud Pipeline

PaperIQ uses a decoupled, event-driven serverless architecture designed for zero idle cost and high scalability.

```text
┌─────────────────┐       S3 Upload      ┌──────────────────┐      Trigger      ┌───────────────────┐
│                 ├─────────────────────>│                  ├──────────────────>│                   │
│  Streamlit UI   │                      │    Amazon S3     │                   │ Ingestion Lambda  │
│  (Cloud/Local)  │                      │                  │                   │                   │
└────────┬────────┘                      └──────────────────┘                   └─────────┬─────────┘
         │                                                                                │
         │ HTTP POST                                                                      │ Embeddings
         ▼                                                                                ▼
┌─────────────────┐     Invoke Payload   ┌──────────────────┐    Query Vector    ┌───────────────────┐
│                 ├─────────────────────>│                  ├───────────────────>│                   │
│   API Gateway   │                      │   Query Lambda   │                    │     Pinecone      │
│                 │                      │                  │<───────────────────┤   Vector Store    │
└─────────────────┘                      └────────┬─────────┘    Context Match   └───────────────────┘
                                                  │
                                                  │ Prompt + Context
                                                  ▼
                                         ┌──────────────────┐
                                         │                  │
                                         │  Gemini AI Model │
                                         │                  │
                                         └──────────────────┘

extract