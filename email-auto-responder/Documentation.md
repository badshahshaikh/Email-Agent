
1. Solution Architecture Document

High-Level Overview: The system uses a Decoupled Client-Server Architecture.

  - The Brain (Server): A FastAPI application (main.py) that hosts the LangGraph
    Orchestrator and Llama 3 model. It exposes a REST API for email analysis.
  - The Hands (Worker): A background process (background_worker.py) that polls a
    Gmail inbox using IMAP. It acts as a client to the FastAPI server and
    handles SMTP replies.
  - The Data (Persistence): A PostgreSQL database storing simulated customer,
    account, and transaction data.

Data Flow: Gmail Inbox → Background Worker → FastAPI Server → LangGraph
Orchestrator → Llama 3 / SQL DB → Response Generator → Worker (SMTP) → Customer
Email.

2. Low-Level Design (LLD)

Core Components:

  - EmailOrchestrator (workflows/orchestrator.py): Manages the state machine
    using LangGraph. It ensures the correct sequence of agent execution.
  - Llama3Agent (agents/llama3_agent.py): Handles the non-deterministic NLP
    tasks (Sentiment, Entities, Summary).
  - ValidationAgent (agents/validation_agent.py): A deterministic security agent
    that verifies sender-account ownership via SQL.
  - APISelectionAgent (agents/api_selection_agent.py): The decision engine that
    maps intents to backend functions and executes them in parallel.
  - BankAPI (apis/bank_services.py): The interface for database operations
    (mocking the Core Banking System).

3. API Specifications

The system exposes the following primary endpoint for email processing:

POST /process-email

  - Description: Processes raw email text and returns structured banking data.
  - Request Body:
    {
      "body": "Hi, what is the balance of my account 1234567890?",
      "sender": "customer@gmail.com"
    }
  - Response (200 OK):
    {
      "customer_name": "John Doe",
      "summary": "Account balance inquiry",
      "sentiment": {"label": "Neutral", "score": 0.0},
      "api_results": [
        {
          "intent": "Account Balance",
          "data": {"account": "1234567890", "balance": 1250.0, "status": "SUCCESS"}
        }
      ]
    }

4. Agent Workflow Document (LangGraph Flow)

The workflow is a directed graph consisting of three primary nodes:

1.  Node: Understanding
      - Agent: Llama 3 + IntentAgent.
      - Task: Parse the raw text to find what the user wants (Intents) and what
        data they provided (Entities).
2.  Node: Validation
      - Agent: ValidationAgent.
      - Task: Compare the sender_email from the email header with the
        owner_email in the PostgreSQL database for the extracted account
        numbers.
3.  Node: API Execution
      - Agent: APISelectionAgent.
      - Task: If validation passes, trigger the corresponding Bank APIs
        (GetBalance, GetStatement, etc.) using a thread pool for parallel
        performance.

5. Assumptions and Limitations

  - Assumptions:
      - The core banking system is simulated via a local PostgreSQL database.
      - Customers have a registered email address in the database used for
        identity verification.
      - Gmail "App Passwords" are used for IMAP/SMTP authentication.
  - Limitations:
      - Local Inference Speed: Processing time is dependent on CPU/GPU power
        (averages 20-40 seconds on standard hardware).
      - Account Discovery: The system currently relies on the user providing
        their account/card number in the email text; it does not "guess"
        accounts based only on the email address for security reasons.
      - MIME Support: Currently optimized for text/plain email bodies. Complex
        HTML signatures might require additional preprocessing.


