# workflows/processor.py
from apis.bank_services import BankAPI
from utils.security import audit_log

class RequestWorkflow:
    def __init__(self, nlp_results):
        self.results = nlp_results
        self.api = BankAPI()
        self.supported_intents = ["Account Balance", "Credit Card Transactions", "Bank Statement"]

    def execute_actions(self):
        final_responses = []
        customer = self.results['entities'].get('customer_name', 'Unknown')
        
        # Get list of intent names from the AI results
        detected_intents = [i['intent'] for i in self.results.get('intents', [])]
        entities = self.results.get('entities', {})

        if not detected_intents:
            return [{"error": "I'm sorry, I couldn't understand your request. Could you please specify if you need a balance, statement, or card transactions?"}]

        for intent in detected_intents:
            # 1. HANDLE ACCOUNT BALANCE
            if intent not in self.supported_intents:
                final_responses.append({"intent": intent, "error": "This specific request type is not supported yet."})
                continue

            if intent == "Account Balance":
                acc = entities['account_numbers'][0] if entities.get('account_numbers') else None
                if not acc:
                    final_responses.append({"intent": intent, "error": "Missing account number."})
                    continue

                validation = self.api.ValidateAccountAPI(acc)
                if validation["status"] != "VALID":
                    final_responses.append({"intent": intent, "error": validation["error"]})
                    continue

                data = self.api.GetAccountBalanceAPI(acc)

                if data["status"] in ["ERROR", "FAILED"]:
                    final_responses.append({"intent": intent, "error": "System error. Please try again later."})
                else:
                    final_responses.append({"intent": intent, "data": data})

                audit_log(customer, intent, data["status"])
            
            elif intent == "Credit Card Transactions":
                card = entities['card_numbers'][0] if entities.get('card_numbers') else None
                if not card:
                    final_responses.append({"intent": intent, "error": "Missing card number."})
                    continue

                validation = self.api.ValidateCardAPI(card)
                if validation["status"] != "VALID":
                    final_responses.append({"intent": intent, "error": validation["error"]})
                    continue

                data = self.api.GetCardTransactionsAPI(card)
                if data["status"] in ["ERROR", "FAILED"]:
                    final_responses.append({"intent": intent, "error": "System error accessing card data."})
                else:
                    final_responses.append({"intent": intent, "data": data})

                audit_log(customer, intent, data["status"])

                # validation = self.api.ValidateCardAPI(card)
                # if validation["status"] != "VALID":
                #     final_responses.append({"intent": intent, "error": validation["error"]})
                #     continue

                # if data["status"] in ["ERROR", "FAILED"]:
                #     final_responses.append({"intent": intent, "error": "System error. Please try again later."})
                # else:
                #     final_responses.append({"intent": intent, "data": data})

                # if acc:
                #     data = self.api.GetAccountBalanceAPI(acc)
                #     final_responses.append({"intent": intent, "data": data})
                #     audit_log(customer, intent, data.get("status", "FAILED"))
                # else:
                #     final_responses.append({"intent": intent, "error": "Missing account number."})


            # 2. HANDLE CREDIT CARD
            # elif intent == "Credit Card Transactions":
            #     card = entities['card_numbers'][0] if entities.get('card_numbers') else None
            #     if card:
            #         data = self.api.GetCardTransactionsAPI(card)
            #         final_responses.append({"intent": intent, "data": data})
            #         audit_log(customer, intent, data.get("status", "FAILED"))
            #     else:
            #         final_responses.append({"intent": intent, "error": "Missing card number."})

            # 3. HANDLE BANK STATEMENT
            elif intent == "Bank Statement":
                acc = entities['account_numbers'][0] if entities.get('account_numbers') else None
                if not acc:
                    final_responses.append({"intent": intent, "error": "Account number required for statement."})
                    continue
                
                validation = self.api.ValidateAccountAPI(acc)
                if validation["status"] != "VALID":
                    final_responses.append({"intent": intent, "error": validation["error"]})
                    continue

                data = self.api.GetStatementAPI(acc)
                if data["status"] in ["ERROR", "FAILED"]:
                    final_responses.append({"intent": intent, "error": "Statement generation failed."})
                else:
                    final_responses.append({"intent": intent, "data": data})

                audit_log(customer, intent, data["status"])

                # acc = entities['account_numbers'][0] if entities.get('account_numbers') else None
                # if acc:
                #     data = self.api.GetStatementAPI(acc)
                #     final_responses.append({"intent": intent, "data": data})
                #     audit_log(customer, intent, data.get("status", "FAILED"))
                # else:
                #     final_responses.append({"intent": intent, "error": "Account number required."})
                    
        return final_responses