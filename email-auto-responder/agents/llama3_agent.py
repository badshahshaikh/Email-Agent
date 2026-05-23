# agents/llama3_agent.py
from llama_cpp import Llama
import json
import re

class Llama3Agent:
    def __init__(self):
        model_path = "models/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
        # Optimized for speed: n_threads should be your CPU cores
        self.llm = Llama(model_path=model_path, n_ctx=2048, n_threads=6, verbose=False)

    def get_llm(self):
        """Getter for the shared model instance"""
        return self.llm

    def process(self, text: str, custom_prompt: str = None):
        # The prompt is the "Brain". It defines all your previous agents in one list of instructions. 

        # print(f"\n[LLM] Analyzing input: {text[:50]}...") 
        print(f"\n[LLM] Analyzing input: {text}...") 
        system_prompt = """
        You are a banking backend AI. Analyze the user's email and return ONLY a JSON object.
        
        EXTRACT THE FOLLOWING:
        1. summary: A 1-sentence summary of the request.
        2. language: The language code (e.g. 'en', 'es', 'hi').
        3. sentiment: {"label": "Positive/Neutral/Negative/Urgent", "score": float}
        4. intents: A list of objects [{"intent": "Account Balance/Bank Statement/Credit Card Transactions", "confidence": float}]
        5. entities: {
            "customer_name": "Full name if found, else 'Not Found'",
            "account_numbers": ["list of 9-12 digit numbers found"],
            "card_numbers": ["list of card numbers found"],
            "date_range": "e.g. Jan 2024 to March 2024, if found"
        }

        STRICT RULES:
        - Return ONLY valid JSON.
        - Do not explain yourself.
        - If data is missing, use null or empty lists.
        - Intents must be a LIST of separate objects. 
        - If the user asks for two things, provide TWO objects in the 'intents' list.
        - Do not combine intents like 'Balance/Statement'. Use separate entries.

        """

        # Correct Llama 3 Prompt Format (No duplicate tokens)
        prompt = f"<|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        
        output = self.llm(prompt, max_tokens=1024, stop=["<|eot_id|>"])
        response_text = output['choices'][0]['text']
        
        print(f"[LLM] Raw Response Generated:\n{response_text}")
        
        # Default safety dictionary to prevent KeyErrors in other files
        default_response = {
            "summary": "Error parsing request",
            "language": "en",
            "sentiment": {"label": "Neutral", "score": 0.0},
            "intents": [],
            "entities": {"customer_name": "Not Found", "account_numbers": [], "card_numbers": []}
        }

        try:
            # Find JSON block using Regex in case Llama adds any text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                # Ensure the 'entities' key exists even if LLM forgot it
                if 'entities' not in parsed:
                    parsed['entities'] = default_response['entities']
                return parsed
            return default_response
        except Exception as e:
            print(f"LLM Response Error: {e}")
            return default_response