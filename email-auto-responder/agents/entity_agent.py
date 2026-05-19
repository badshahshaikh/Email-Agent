# import re
# import spacy
# from .base_agent import BaseAgent

# class EntityAgent(BaseAgent):
#     def __init__(self):
#         self.nlp = spacy.load("en_core_web_sm")

#     def process(self, text: str):
#         doc = self.nlp(text)
#         return {
#             "customer_name": next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "Not Found"),
#             "account_numbers": re.findall(r'\b\d{9,12}\b', text),
#             "card_numbers": re.findall(r'\b[\dX]{10,16}\b', text),
#             "dates": re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}', text, re.I)
#         }


import re
import spacy
from .base_agent import BaseAgent

class EntityAgent(BaseAgent):
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def process(self, text: str):
        doc = self.nlp(text)
        
        # --- BASE PATTERNS ---
        # Pattern for single date like "April 2024"
        date_regex = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}'
        
        # 1. EXTRACT TRANSACTION COUNT (New)
        # Looks for "last 5", "top 10", "past 3" followed by optional "transactions/charges"
        count_pattern = r'(?:last|top|past|recent|final)\s+(\d{1,2})'
        counts = re.findall(count_pattern, text, re.I)

        # 2. EXTRACT DATE RANGE (Improved)
        # Looks for "Jan 2024 to Mar 2024" or "between Jan 2024 and Mar 2024"
        range_pattern = fr'({date_regex})\s*(?:to|and|until|-|through)\s*({date_regex})'
        ranges = re.findall(range_pattern, text, re.I)

        # 3. EXTRACT INDIVIDUAL DATES (Existing)
        individual_dates = re.findall(date_regex, text, re.I)

        return {
            "customer_name": next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "Not Found"),
            "account_numbers": re.findall(r'\b\d{9,12}\b', text),
            "card_numbers": re.findall(r'\b[\dX]{10,16}\b', text),
            
            # --- NEW FIELDS ---
            "transaction_count": int(counts[0]) if counts else 5, # Default to 5 if not found
            "date_range": {
                "start": ranges[0][0],
                "end": ranges[0][1]
            } if ranges else "Not Found",
            
            "individual_dates": individual_dates
        }