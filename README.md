# RAG Customer Support Automation (PoC)

A Retrieval-Augmented Generation (RAG) based customer support automation proof-of-concept that retrieves relevant knowledge, detects user intent, and applies confidence-based automation with a human-in-the-loop workflow.

## 📌 Overview

This project demonstrates how **Retrieval-Augmented Generation (RAG)** can be combined with
**rule-based intent detection** and **automation workflows** for customer support scenarios.

Instead of auto-sending responses, the system:
- Retrieves relevant knowledge from support documents
- Detects the intent of the user query
- Applies confidence-based automation rules
- Creates **persisted email drafts** or **escalates** the issue for human review

The design prioritizes **safety, auditability, and explainability** over blind automation.
## ✨ Key Features

- 🔍 **Semantic Knowledge Retrieval (RAG)** using vector search
- 🧠 **Rule-Based Intent Detection** (e.g., password reset, refund, payment issue)
- 📊 **Confidence-Based Automation Decisions**
- ✉️ **Draft-Based Email Workflow** (no unsafe auto-sending)
- 👩‍💻 **Human-in-the-Loop Design** for approvals and escalation
- ⚡ **FastAPI Backend** with Swagger UI for testing
- 🧩 **Pluggable Index Backends** (FAISS / sklearn)


## 🏗️ System Architecture


User Query
↓
FastAPI API Endpoint
↓
Vector Search (FAISS / sklearn)
↓
Top-K Context Retrieval
↓
Intent Detection
↓
Confidence-Based Automation Rules
↓
Draft Creation OR Escalation
↓
Human Review / Approval


This architecture explicitly separates **decision-making** from **execution**, which is critical for safe automation systems.

## 🎯 Purpose

Customer support automation often fails due to unsafe auto-responses and lack of human oversight.
This project explores a **safe automation approach** by combining:

- Retrieval-Augmented Generation (RAG) for factual grounding
- Explicit intent detection instead of opaque LLM decisions
- Confidence-based rules to gate automation
- Human-in-the-loop workflows for approvals and escalation

The goal is to demonstrate **production-aligned design thinking**, not blind automation.

## 📁 Project Structure

src/
├── app_faiss.py # FastAPI application entry point
├── intent_detector.py # Rule-based intent detection
├── automation_rules.py # Confidence-based decision logic
├── automation_executor.py # Executes automation actions
├── draft_store.py # Draft persistence & workflow state
├── email_adapter.py # Simulated email sender (outbox)
├── ticket_schema.py # Support ticket models
sample_docs/ # Knowledge base documents
requirements.txt # Python dependencies
.gitignore
README.md

## 🧪 How to Run

### 1. Setup Environment

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### 2. Start the API Server

uvicorn src.app_faiss:app --reload

### 3. Open Swagger UI:
http://127.0.0.1:8000/docs

### 4.Build the Vector Index
POST /rebuild

### 5. Query the System
{
  "query": "How do I reset my account password?",
  "user_email": "user@example.com"
}
The response includes:
detected intent
confidence score
automation decision
draft path or escalation details

### 📤 Example Response

```json
{
  "query": "How do I reset my account password?",
  "intent": "password_reset",
  "confidence": 0.62,
  "decision": "SAVE_DRAFT",
  "automation": {
    "draft_path": "drafts/draft_<ticket_id>.json"
  }
}

## 🧩 Design Decisions

This project intentionally avoids fully automated email sending.

Key design choices:
- **No blind auto-responses**: Automated replies can be risky in customer support.
- **Confidence-gated actions**: Automation decisions depend on retrieval confidence.
- **Human-in-the-loop workflow**: Drafts are persisted and require approval before any real action.
- **Explainable logic**: Intent detection and automation rules are rule-based, not hidden inside LLM prompts.

These decisions reflect how real-world support systems balance automation with safety.

## 🔮 Future Extensions

The current implementation is a proof-of-concept. Possible extensions include:

- Gmail API integration for real draft creation and sending
- LLM-based response generation on top of retrieved context
- Admin dashboard for managing approvals and escalations
- Integration with ticketing systems (Zendesk, Jira, etc.)
- Confidence-based auto-approval for low-risk queries

These features are intentionally not enabled by default to keep the system safe and auditable.

