# workflows/response_generator.py
from utils.formatter import mask_number, format_currency

class ResponseGenerator:
    @staticmethod
    def generate(customer_name, api_results):
        name = customer_name if customer_name != "Not Found" else "Customer"
        
        # Header
        email_body = f"Dear {name},\n"
        email_body += "We have processed your request successfully.\n\n"

        # Content Logic
        for res in api_results:
            intent = res.get('intent')
            data = res.get('data')
            error = res.get('error')

            if intent == "Account Balance":
                if error:
                    email_body += f"Regarding your Balance: {error}\n\n"
                else: 
                    # email_body += f"Account Balance ({mask_number(data['account'])}): {format_currency(data['balance'])}\n\n"
                    email_body += f"Account Number: {mask_number(data['account'])}\n"
                    email_body += f"Available Balance: {format_currency(data['balance'])}\n\n"



            elif intent == "Credit Card Transactions":
                email_body += "Credit Card Request:\n" 
                if error:
                    # Cleaner error formatting
                    email_body += "The credit card number provided could not be validated. Kindly recheck the card details and resend your request.\n\n"
                else:
                    # email_body += f"Recent Transactions for Card {mask_number(data['card'])}:\n"
                    # for tx in data['transactions']:
                    #     email_body += f"- {tx['date']}: {tx['description']} ({format_currency(tx['amount'])})\n"
                    # email_body += "\n"

                    email_body += f"Card Number: {mask_number(data['card'])}\n"
                    email_body += "Recent Transactions:\n"
                    for tx in data['transactions']:
                        email_body += f"- {tx['date']}: {tx['description']} ({format_currency(tx['amount'])})\n"
                    email_body += "\n"


            elif intent == "Bank Statement":
                if error:
                    email_body += f"Regarding your Statement: {error}\n\n"
                else:
                    # 'document' key is now safe because of the API fix
                    # email_body += f"Your statement for account {mask_number(data['account'])} is ready. Reference ID: {data.get('document', 'N/A')}\n\n" 
                    email_body += f"Account Number: {mask_number(data['account'])}\n"
                    email_body += f"Your statement for the requested period is ready. (Ref: {data.get('document', 'N/A')})\n\n"


        # Footer
        # email_body += "Thank you for banking with us,\nCustomer Support Team"
        email_body += "Thank you,\n"
        email_body += "Customer Support Team"

        return email_body