# agents/task_analysis_agent.py
from .base_agent import BaseAgent

class TaskAnalysisAgent(BaseAgent):
    def __init__(self, classifier):
        self.classifier = classifier
        # We give the AI labels that describe the "count" of tasks
        self.labels = [
            "a single bank service request", 
            "multiple different bank service requests"
        ]


    def process(self, text: str):
        hypothesis = "This email contains {}."

        result = self.classifier(
            text, 
            self.labels, 
            multi_label=False, 
            hypothesis_template=hypothesis
        )

        detected_label = result['labels'][0]
        
        # Clean up the output for your report
        complexity_map = {
            "a single bank service request": "single request",
            "multiple different bank service requests": "multiple requests"
        }

        return {
            "task_complexity": complexity_map.get(detected_label, "unknown"),
            "confidence": round(result['scores'][0], 2)
        }
