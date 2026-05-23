# agents/api_selection_agent.py
import concurrent.futures
from apis.bank_services import BankAPI

class APISelectionAgent:
    def __init__(self):
        self.bank_api = BankAPI()
        self.supported_intents = ["Account Balance", "Credit Card Transactions", "Bank Statement"]

    def process(self, state):
        print("--- Node: API Selection Agent (Decision Engine) ---")
        results = []
        intents_list = state.get('intents') or []
        intents = [i['intent'] for i in intents_list if i and 'intent' in i]

        # intents = [i['intent'] for i in state.get('intents', [])]
        # entities = state.get('entities', {})
        # authorized_accs = state['validation_results'].get('authorized_accounts', [])

        entities = state.get('entities') or {}
        val_results = state.get('validation_results') or {}
        authorized_accs = val_results.get('authorized_accounts') or []


        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_intent = {}

            for intent in intents:
                if intent not in self.supported_intents:
                    results.append({"intent": intent, "error": "Not supported"})
                    continue

                if isinstance(intent, dict):
                    raw_intent = intent.get('intent', "").lower()
                else:
                    raw_intent = str(intent).lower()
                


                # raw_intent = intent.get('intent', "").lower()

                # Decision Logic moved from processor.py
                # if intent == "Account Balance":
                if "balance" in raw_intent:

                    # acc = entities['account_numbers'][0] if entities.get('account_numbers') else None
                    acc_list = entities.get('account_numbers') or []
                    acc = acc_list[0] if acc_list else None

                    if acc and acc in authorized_accs:
                        future_to_intent[executor.submit(self.bank_api.GetAccountBalanceAPI, acc)] = "Account Balance"
                    else:
                        results.append({"intent": "Account Balance", "error": "Access Denied: Unauthorized or invalid account number."})


                # elif intent == "Bank Statement":
                if "statement" in raw_intent and "card" not in raw_intent:

                    # acc = entities['account_numbers'][0] if entities.get('account_numbers') else None
                    acc_list = entities.get('account_numbers') or []
                    acc = acc_list[0] if acc_list else None

                    # if acc in authorized_accs:
                    #     future_to_intent[executor.submit(self.bank_api.GetStatementAPI, acc)] = intent
                    # else:
                    #     results.append({
                    #                 "intent": intent, 
                    #                 "error": "Access Denied: You are not authorized to view this account."
                    #             })
                    if acc and acc in authorized_accs:
                        future_to_intent[executor.submit(self.bank_api.GetStatementAPI, acc)] = "Bank Statement"
                    else:
                        results.append({"intent": "Bank Statement", "error": "Access Denied: Authorized account required for statements."})


                # elif intent == "Credit Card Transactions":
                if "card" in raw_intent or "transaction" in raw_intent:
                    card_list = entities.get('card_numbers') or []
                    card = card_list[0] if card_list else None

                    # card = entities['card_numbers'][0] if entities.get('card_numbers') else None
                    # if card: # Assuming card validation is separate or handled
                    #     future_to_intent[executor.submit(self.bank_api.GetCardTransactionsAPI, card)] = intent

                    if card:
                        # SCENARIO 5: Explicitly validate the card
                        validation = self.bank_api.ValidateCardAPI(card)
                        if validation["status"] == "VALID":
                            future_to_intent[executor.submit(self.bank_api.GetCardTransactionsAPI, card)] = "Credit Card Transactions"
                        else:
                            # If card is invalid, we add the error but DON'T stop the loop
                            results.append({"intent": "Credit Card Transactions", "error": "Invalid Card"})
                    else:
                        results.append({"intent": "Credit Card Transactions", "error": "Missing card number."})



            # Collect parallel results
            for future in concurrent.futures.as_completed(future_to_intent):
                intent_name = future_to_intent[future]
                try:
                    data = future.result()
                    results.append({"intent": intent_name, "data": data})
                except Exception as e:
                    results.append({"intent": intent_name, "error": str(e)})

        return {"api_results": results}