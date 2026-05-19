
from transformers import pipeline
from agents.intent_agent import IntentAgent
from agents.sentiment_agent import SentimentAgent
from agents.entity_agent import EntityAgent
from agents.summarizer_agent import SummarizerAgent
# from agents.task_analysis_agent import TaskAnalysisAgent

class EmailOrchestrator:
    def __init__(self):
        print("Loading AI Models...") 
        # Share one model instance for memory efficiency
        bart_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        
        # Dependency Injection
        self.agents = {
            "summary": SummarizerAgent(),
            "intents": IntentAgent(),
            "sentiment": SentimentAgent(bart_classifier),
            "entities": EntityAgent()
        }

    def analyze(self, text: str):

        # 1. Summarize first
        summary = self.agents['summary'].process(text)
        
        # 2. Provide ONLY the summary to the other agents
        intent = self.agents['intents'].process(text)
        sentiment = self.agents['sentiment'].process(text)
        
        # 3. BUT you still need original text for Entities (Numbers/Names)
        entities = self.agents['entities'].process(text) 

        # self.task_counter_agent = TaskAnalysisAgent(model)
        # task_complexity = self.agents['task_complexity'].process(summary)


        return {
            "summary": summary,
            "intents": intent,
            "sentiment": sentiment,
            "entities": entities
        }