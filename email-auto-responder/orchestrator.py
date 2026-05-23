# orchestrator.py
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from agents.intent_agent import IntentAgent
from agents.entity_agent import EntityAgent
from agents.validation_agent import ValidationAgent
from agents.sentiment_agent import SentimentAgent
from agents.llama3_agent import Llama3Agent
from agents.api_selection_agent import APISelectionAgent
from utils.security import audit_log
# from agents.api_selection_agent import node_execute_banking

# from agents.language_agent import LanguageAgent # Keep this for fast detection

# 1. Define the State (The data that flows through the graph)
class AgentState(TypedDict):
    # raw_text: str
    # language: str
    # analysis: Dict
    raw_body: str      # Added
    raw_subject: str   # Added
    sender_email: str
    intents: List[Dict]
    entities: Dict
    sentiment: Dict
    validation_results: Dict
    api_results: List[Dict]
    summary: str
    final_response: str

class EmailOrchestrator:
    def __init__(self):
        self.validation_agent = ValidationAgent()
        self.llama_agent = Llama3Agent()
        # self.intent_agent = IntentAgent(llama_agent=self.llama_agent)
        self.api_selector = APISelectionAgent()

        workflow = StateGraph(AgentState)

        workflow.add_node("understanding", self.node_understand_email)
        workflow.add_node("validation", self.node_validate_security)
        workflow.add_node("api_execution", self.node_execute_banking)

        workflow.set_entry_point("understanding")
        workflow.add_edge("understanding", "validation")
        workflow.add_edge("validation", "api_execution")
        workflow.add_edge("api_execution", END)

        self.app = workflow.compile()

    def node_understand_email(self, state: AgentState):
        print("--- Node: Understanding ---")
        # text = state['raw_text']
        llama_results = self.llama_agent.process(state['raw_body'], state['raw_subject'])

        # intents = self.intent_agent.process(text)

        entities = llama_results.get('entities')
        if not isinstance(entities, dict):
            entities = {"customer_name": "Not Found", "account_numbers": [], "card_numbers": []}

        sentiment = llama_results.get('sentiment')
        if not isinstance(sentiment, dict):
            sentiment = {"label": "Neutral", "score": 0.0}

        intents = llama_results.get('intents', [])


        audit_log("AI_UNDERSTANDING", "COMPLETED", f"Found {len(llama_results.get('intents', []))} intents")

        # return {
        #     "intents": llama_results.get('intents', []),
        #     "entities": llama_results.get('entities', {}),
        #     "sentiment": llama_results.get('sentiment', {}),
        #     "summary": llama_results.get('summary', "")
        # }
        return {
            "intents": intents,
            "entities": entities,
            "sentiment": sentiment,
            "summary": llama_results.get('summary', "No summary available")
        }




    def node_validate_security(self, state: AgentState):
        print("--- Node: Security Validation ---")
        sender = state['sender_email']
        # acc_nums = state['entities'].get('account_numbers', [])
        
        # valid_accounts = []
        # for acc in acc_nums:
        #     if self.validation_agent.verify_ownership(sender, acc):
        #         valid_accounts.append(acc)
        entities = state.get('entities') or {}
        acc_nums = entities.get('account_numbers') or [] 

        
        # return {"validation_results": {"authorized_accounts": valid_accounts}}
        authorized = [
            acc for acc in acc_nums 
            if self.validation_agent.verify_ownership(sender, acc)
        ]
        
        audit_log("VALIDATION_NODE", "INFO", f"Sender: {sender} | Accounts: {acc_nums} | Authorized: {authorized}")
        return {"validation_results": {"authorized_accounts": authorized}}


    def node_execute_banking(self, state: AgentState):
        print("--- Node: API Execution ---")
        # Logic from processor.py moves here to execute ONLY authorized accounts
        # ... logic to call GetAccountBalanceAPI only if authorized ...
        return self.api_selector.process(state)


    def node_llama_processor(self, state: AgentState):
        print("--- Node: Llama 3 All-in-One Analysis ---")
        # LLM performs intent, sentiment, entities, summary, and language at once
        res = self.llama_agent.process(state['raw_text'])
        return {"analysis": res}


    # def analyze(self, text: str):
    #     # Entry point for main.py
    #     initial_state = {"raw_text": text, "analysis": {}}
    #     final_state = self.app.invoke(initial_state)
    #     return final_state['analysis']
    
    def analyze(self,body: str, subject: str, sender: str):
        # initial_state = {"raw_text": text, "sender_email": sender}
        # return self.app.invoke(initial_state)
        initial_state = {
            "raw_body": body, 
            "raw_subject": subject,
            "sender_email": sender,
            "intents": [],
            "entities": {},
            "sentiment": {},
            "validation_results": {},
            "api_results": [],
            "summary": "",
            "final_response": ""
        }
        return self.app.invoke(initial_state)
    


