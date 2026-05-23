# agents/language_agent.py
from transformers import pipeline
from .base_agent import BaseAgent

class LanguageAgent(BaseAgent):
    def __init__(self):
        # State of the art language detection (supports 20+ languages)
        print("Loading Language Detection Model...")
        self.detector = pipeline(
            "text-classification", 
            model="papluca/xlm-roberta-base-language-detection"
        )

    def process(self, text: str):
        if not text:
            return {"language": "en", "score": 1.0}
            
        result = self.detector(text[:512])[0] # Process first 512 chars
        return {
            "language": result['label'], # e.g., 'es', 'fr', 'en'
            "score": round(result['score'], 4)
        }