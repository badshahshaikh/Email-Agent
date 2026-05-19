# workflows/processor.py
from apis.bank_services import BankAPI
from utils.security import audit_log

class RequestWorkflow:
    def __init__(self, nlp_results):
        self.results = nlp_results
        self.api = BankAPI()

    def execute_actions(self):
        final_responses = []
        customer = self.results['entities'].get('customer_name', 'Unknown')
        
        # Get list of intent names from the AI results
        detected_intents = [i['intent'] for i in self.results.get('intents', [])]
        entities = self.results.get('entities', {})

        for intent in detected_intents:
            # 1. HANDLE ACCOUNT BALANCE
            if intent == "Account Balance":
                acc = entities['account_numbers'][0] if entities.get('account_numbers') else None
                if acc:
                    data = self.api.get_balance(acc)
                    final_responses.append({"intent": intent, "data": data})
                    audit_log(customer, intent, "SUCCESS")
                else:
                    final_responses.append({"intent": intent, "error": "Missing account number. Please provide your 10-digit account number."})

            # 2. HANDLE CREDIT CARD
            elif intent == "Credit Card Transactions":
                card = entities['card_numbers'][0] if entities.get('card_numbers') else None
                if card:
                    data = self.api.get_transactions(card)
                    final_responses.append({"intent": intent, "data": data})
                    audit_log(customer, intent, "SUCCESS")
                else:
                    final_responses.append({"intent": intent, "error": "Missing card number. Please provide your card number for verification."})

            # 3. HANDLE BANK STATEMENT
            elif intent == "Bank Statement":
                acc = entities['account_numbers'][0] if entities.get('account_numbers') else None
                if acc:
                    data = self.api.get_statement(acc)
                    final_responses.append({"intent": intent, "data": data})
                    audit_log(customer, intent, "SUCCESS")
                else:
                    final_responses.append({"intent": intent, "error": "Account number required to generate statement."})
                    
        return final_responses