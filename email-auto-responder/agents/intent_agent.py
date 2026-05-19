from sentence_transformers import SentenceTransformer, util
import torch
import re
from .base_agent import BaseAgent

class IntentAgent(BaseAgent):
    def __init__(self, classifier=None):
        self.classifier = classifier
        # 1 - check account balance
        # 2 - request account statement
        # 3 - check credit card usage
        # 4 - request credit card statement
        # self.labels = [
        #     "account balance request", 
        #     "bank statement request", 
        #     "credit card transactions request"
        # ]

        print("Loading Intent Model (all-mpnet-base-v2)...")
        self.model = SentenceTransformer('all-mpnet-base-v2')
        
        self.intent_anchors = {
            "Account Balance": [
                "What is my current available balance?",
                "How much money is in my savings account?",
                "Show my total available funds.",
                "I want to check my account balance."
            ],
            "Bank Statement": [
                "Send me a bank statement document.",
                "I need my monthly transaction history report.",
                "Requesting an account statement PDF.",
                "Provide my bank statement for the month."
            ],
            "Credit Card Transactions": [
                "Show my recent credit card spending.",
                "List the transactions on my credit card.",
                "Check my last few card charges.",
                "View credit card usage history."
            ]
        }
        
        # Pre-calculate embeddings to save time during processing
        self.anchor_embeddings = {
            k: self.model.encode(v, convert_to_tensor=True) 
            for k, v in self.intent_anchors.items()
        }

        



    def process(self, text: str):
        # result = self.classifier(text, self.labels, multi_label=True)
        # detected_intents = []
        
        # for label, score in zip(result['labels'], result['scores']):
        #     if score > 0.5: 
        #         detected_intents.append({
        #             "intent": label,
        #             "confidence": round(score, 4) # Rounding to 4 decimal places
        #         })

        if not text:
            return []

        
        # return detected_intents
        # Split text to handle multi-intent emails
        parts = re.split(r' and | also |, ', text)
        final_results = {}

        for part in parts:
            part_embedding = self.model.encode(part, convert_to_tensor=True)
            part_scores = []
            
            for intent, anchors in self.anchor_embeddings.items():
                scores = util.cos_sim(part_embedding, anchors)
                max_score = torch.max(scores).item()
                part_scores.append((intent, max_score))
            
            # Sort scores to find the best match
            part_scores.sort(key=lambda x: x[1], reverse=True)            
            best_intent, best_score = part_scores[0]
            
            # Threshold and Logic Overrides
            if best_score > 0.40:
                # Priority Rule: If 'balance' is mentioned, ensure it's categorized correctly
                if "balance" in part.lower():
                    bal_score = next(s for i, s in part_scores if i == "Account Balance")
                    if bal_score > 0.35:
                        best_intent = "Account Balance"
                        best_score = bal_score

                # Save the highest score for each unique intent found in the email
                if best_intent not in final_results or best_score > final_results[best_intent]:
                    final_results[best_intent] = best_score

        # Format output for the Rich Report in main.py
        return [
            {"intent": name, "confidence": round(score, 4)} 
            for name, score in final_results.items()
        ]

    