# apis/bank_services.py
import time
import random

class BankAPI:
    @staticmethod
    def validate_account(acc_num):
        # Simulate API call
        if not acc_num or len(acc_num) < 10:
            return {"status": "INVALID", "error": "Account number too short"}
        return {"status": "VALID", "customer_name": "John Doe"}

    @staticmethod
    def get_balance(acc_num):
        try:
            # Simulate a timeout check
            time.sleep(0.5) 
            return {"account": acc_num, "balance": 5420.50, "currency": "USD"}
        except Exception:
            return {"error": "API Timeout", "status": "FAILED"}

    @staticmethod
    def get_transactions(card_num):
        # Simulate card masking and fetching
        return {
            "card": f"XXXX-XXXX-XXXX-{card_num[-4:]}",
            "transactions": [
                {"date": "2024-05-18", "amount": -50.00, "desc": "Starbucks"},
                {"date": "2024-05-17", "amount": -120.00, "desc": "Amazon"}
            ]
        }
    
    @staticmethod
    def get_statement(acc_num):
        return {"account": acc_num, "document": "statement_feb_2024.pdf", "status": "SUCCESS"}
