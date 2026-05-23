# utils/translator.py
from transformers import pipeline

class TranslationService:
    def __init__(self):
        # This model supports 100+ languages to English
        print("Loading Translation Model (M2M100)...")
        self.translator = pipeline("translation", model="facebook/m2m100_418M")

    def translate_to_english(self, text: str, src_lang: str) -> str:
        if src_lang == "en":
            return text
        
        # Translate from detected language to English
        result = self.translator(text, src_lang=src_lang, tgt_lang="en")
        return result[0]['translation_text']