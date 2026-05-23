from orchestrator import EmailOrchestrator
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from orchestrator import EmailOrchestrator
from workflows.processor import RequestWorkflow
from utils.db_initializer import initialize_database
from contextlib import asynccontextmanager
from config.db_pool import DatabasePool
from apis.bank_services import BankAPI
from apis.bank_routes import router as bank_router
from utils.security import audit_log
bot = EmailOrchestrator()
console = Console()
bank_api = BankAPI()

class EmailRequest(BaseModel):
    body: str
    sender: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the app starts
    print("Starting up: Initializing Database...")
    initialize_database()
    DatabasePool.get_pool() 
    yield
    # This runs when the app shuts down
    print("Shutting down...")
    DatabasePool.close_all()


app = FastAPI(title="Banking AI Agent API", lifespan=lifespan)

app.include_router(bank_router)


@app.get("/")
async def root():
    return {"message": "Banking AI System is online", "docs": "/docs"}



@app.post("/process-email")
async def process_email(request: EmailRequest):
    
    try:
        
        audit_log("API_CALL", "STARTED", f"Processing email with body: {request.body[:50]}...")  # Log the start of processing

        final_state = bot.analyze(request.body, request.sender)

        audit_log("API_CALL", "FINAL_ANALYSIS", f"Final analysis for email: {final_state}")

        # entities = final_state.get('entities') or {}
        # sentiment = final_state.get('sentiment') or {"label": "Neutral", "score": 0.0}

        res_entities = final_state.get('entities') or {}
        if not isinstance(res_entities, dict): res_entities = {}
        
        res_sentiment = final_state.get('sentiment') or {}
        if not isinstance(res_sentiment, dict): res_sentiment = {"label": "Neutral"}

        return {
            "customer_name": res_entities.get('customer_name', 'Not Found'),
            "summary": final_state.get('summary', 'Processed'),
            "sentiment": res_sentiment,
            "api_results": final_state.get('api_results') or []
        }



    except Exception as e:
        audit_log("API_CALL", "ERROR", f"Error processing email: {str(e)}")
        print(f"Error processing email: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        


def print_agent_report(output):
    """Prints a beautiful formatted report of the AI analysis"""
    
    # 1. Create a Metadata Table
    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Category", style="dim", width=20)
    table.add_column("Information", style="white")

    table.add_row("Customer Name", output['entities']['customer_name'])
    
    # Color code sentiment
    sentiment_color = "green" if "Positive" in output['sentiment']['label'] else "yellow"
    if "Negative" in output['sentiment']['label'] or "Urgent" in output['sentiment']['label']:
        sentiment_color = "red"
    
    table.add_row("Tone / Sentiment", f"[{sentiment_color}]{output['sentiment']['label']}[/{sentiment_color}]")
    # table.add_row("Task Complexity", f"[cyan]{output['task_complexity']}[/cyan]")
    
    if output['intents']:
        intents_list = [f"{i['intent']} ({int(i['confidence']*100)}%)" for i in output['intents']]
        intents_str = ", ".join(intents_list)
    else:
        intents_str = "None"

    table.add_row("AI Intents Found", intents_str)
    
    summary_label = Text("Summary:\n", style="bold white")
    summary_content = Text(output['summary'] + "\n", style="italic yellow")


    report_content = Group(
        summary_label,
        summary_content,
        Text("\n"),
        table
    )

    main_panel = Panel(
        report_content,
        title="[bold cyan]Email Agent Analysis Report[/bold cyan]",
        subtitle="[dim]Banking Auto-Responder v1.0[/dim]",
        border_style="blue",
        padding=(1, 2)
    )

    console.print("\n")
    console.print(main_panel)


# def main():
#     bot = EmailOrchestrator()
    
#     # email = "Hi, I am John Doe. I am very frustrated. Please send my statement for April 2026."

#     email = [
#         "Please provide my savings account balance for account number 1234567890.", 
#         "Please share my last 5 credit card transactions for card 4567XXXX8901.",   
#         "Kindly send my bank statement for April 2026.", 
#         "Please share my account balance for account 1234567890 and also send last 3 transactions of my credit card 987654321.", 
#         "Please provide balance for account 1234567890 and card transactions for card 999999999.",
#         "Hi team, can you please tell me how much money is currently in my savings account?",
#         "Hey, I just want to check my available balance before I go shopping.",
#         "Could you let me know my account balance? I am waiting for my salary to be credited.",
#         "Quick check on my funds, please let me know the total in my main account.",
#         "I'm trying to see if a check cleared, what is my current balance right now?",
#         "Is it possible to see the available funds for my account ending in 1234?",
#         "I need a quick update on my savings total.",
#         "How much cash do I have left in my account today?",
#         "Please provide the current standing of my bank account balance.",
#         "Can I get a balance check for my primary savings?",
#         "I need to apply for a visa, can you please send me my bank statement for the last 3 months?",
#         "Kindly share the transaction history report for my account for the month of April.",
#         "I am looking for my bank statement from January to March. Please send it as a PDF.",
#         "Could you provide a copy of my latest account statement? I need it for my records.",
#         "Hi, I need to download my bank statement for the previous month. How can I get it?",
#         "Please send over the historical record of my transactions for the year 2023.",
#         "I need a bank statement document for my mortgage application. Please send it to my email.",
#         "Can you provide the monthly statement for my savings account?",
#         "I'm looking for a summary of my account activity for last July.",
#         "Please generate a statement report for my account for the last 30 days.",
#         "I noticed a weird charge on my card. Can you show me my recent credit card transactions?",
#         "Please share the spending history for my credit card for the past week.",
#         "I want to check my credit card usage. What are the last 5 things I bought?",
#         "Can you list the latest charges on my credit card ending in 9901?",
#         "I need to see my credit card transactions to verify some payments I made.",
#         "What is the current spending on my card? Show me the transaction list.",
#         "Please provide a breakdown of my credit card activity for this billing cycle.",
#         "I need to check my card usage history for the last 10 days.",
#         "Show me my most recent credit card purchases, please.",
#         "What are the transactions on my card for yesterday?",
#         "Please send my bank statement and also tell me my current balance.",
#         "I need to check my card transactions and my savings balance as well.",
#         "Can you provide my account balance and send the statement for May?",
#         "I want to see my card usage and also get a PDF of my bank statement."
#     ]

#     print("--- Processing Email ---")

#     for email in email:
#         output = bot.analyze(email)
#         print_agent_report(output)

if __name__ == "__main__":
    # main()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
