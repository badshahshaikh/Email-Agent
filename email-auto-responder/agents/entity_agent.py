import re
import spacy
from .base_agent import BaseAgent

class EntityAgent(BaseAgent):
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def process(self, text: str):
        doc = self.nlp(text)
        return {
            "customer_name": next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "Not Found"),
            "account_numbers": re.findall(r'\b\d{9,12}\b', text),
            "card_numbers": re.findall(r'\b[\dX]{10,16}\b', text),
            "dates": re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}', text, re.I)
        }
