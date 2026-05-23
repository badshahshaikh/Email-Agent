# Intelligent Banking Email Automation System

An AI-powered system that uses Llama 3 and Agentic AI (LangGraph) to process banking emails, identify customer intents, and generate automated responses.

## Key Features
- **Agentic Workflow:** Specialized agents for Intent, Entities, Validation, and Decision making.
- **Security:** Verifies sender email against account ownership before releasing data.
- **Parallel Processing:** Executes multiple API calls (Balance + Transactions) simultaneously.
- **Partial Failure Handling:** Intelligently handles valid accounts with invalid card numbers.

## Technology Stack
- **AI:** Llama 3 (3B-Instruct), LangGraph
- **API:** FastAPI
- **DB:** PostgreSQL
- **Email:** IMAP/SMTP

## Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Download Llama 3 GGUF model to the `models/` folder.
4. Set up your `.env` file based on `.env.example`.

## How to Run

### Option 1: One-Click Startup (Recommended)
If you are on Windows, simply double-click the launcher script in the root directory:
- **File:** `run.bat`

This will automatically open two separate terminal windows:
1. **AI-SERVER:** Runs the FastAPI backend and loads the Llama 3 model.
2. **EMAIL-WORKER:** Runs the email polling and response logic.

---

## Required Test Setup (Important)

For the **Security Validation Agent** to authorize your requests, the sender's email address must match the record in the database. 

Before testing, please update the mock database with your testing email address:

1. **Open your Database Tool** (e.g., pgAdmin, psql).
2. **Run the following SQL command** (replace `your-email@gmail.com` with the email you will use to send requests):

```sql
-- Update the mock customer email to your testing email
UPDATE customers 
SET email = 'your-email@gmail.com' 
WHERE id = 1;

-- This links account '1234567890' to your email for Scenario 1, 4, and 5.


## 📂 Folder Structure
project/
│
├── agents/
├── apis/
├── models/
├── prompts/
├── workflows/
├── utils/
├── tests/
├── config/
├── logs/
├── main.py
├── requirements.txt
└── README.md

