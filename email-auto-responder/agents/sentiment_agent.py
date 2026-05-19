from .base_agent import BaseAgent

class SentimentAgent(BaseAgent):
    def __init__(self, classifier):
        self.classifier = classifier
        self.labels = ["Positive", "Neutral", "Negative / Angry Customer", "Urgent / Escalation"]

    def process(self, text: str):
        result = self.classifier(text, self.labels, multi_label=False)
        return {"label": result['labels'][0], "score": round(result['scores'][0], 2)}
    