from .base_agent import BaseAgent
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class SummarizerAgent(BaseAgent):
    def __init__(self):
        # We load model and tokenizer manually to bypass the Pipeline Task Registry error
        self.model_name = "sshleifer/distilbart-cnn-12-6"
        print(f"Loading Summarizer Model: {self.model_name}...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

    def process(self, text: str):
        # 1. Skip if text is too short
        if len(text.split()) < 20:
            return text

        # 2. Tokenize the input text
        # truncation=True ensures we don't crash on extremely long emails
        inputs = self.tokenizer([text], max_length=1024, return_tensors="pt", truncation=True)

        # 3. Generate the summary
        # num_beams=4 makes the summary higher quality
        summary_ids = self.model.generate(
            inputs["input_ids"], 
            num_beams=4, 
            max_length=50, 
            min_length=10, 
            early_stopping=True
        )

        # 4. Decode the summary back into readable text
        summary = self.tokenizer.batch_decode(
            summary_ids, 
            skip_special_tokens=True, 
            clean_up_tokenization_spaces=False
        )[0]
        
        return summary