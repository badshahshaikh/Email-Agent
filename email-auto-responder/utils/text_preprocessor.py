# utils/text_preprocessor.py
import re

class TextPreprocessor:
    @staticmethod
    def clean(text: str) -> str:
        """
        Main pipeline to normalize email body text.
        """
        if not text:
            return ""

        # 1. Remove quoted replies (lines starting with '>')
        # Common in email chains
        text = re.sub(r'(?m)^>.*$', '', text)

        # 2. Remove email signatures
        # Looks for common separators like '--' or 'Regards,' and cuts everything after
        signature_patterns = [
            r'--\s*$',               # Standard dash signature
            r'Regards,.*$',          # Common closings
            r'Best regards,.*$',
            r'Sincerely,.*$',
            r'Sent from my .*$'      # Mobile phone signatures
        ]
        for pattern in signature_patterns:
            # We split the text and keep only the first part (the content)
            parts = re.split(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
            text = parts[0]

        # 3. Standardize whitespace
        # Replace newlines, tabs, and multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)

        # 4. Remove non-text artifacts (URLs/Special characters)
        # We keep alphanumeric and basic punctuation for the Intent Agent
        text = re.sub(r'http\S+', '', text) # Remove URLs

        return text.strip()