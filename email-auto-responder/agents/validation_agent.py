# from apis.bank_services import BankAPI

# class ValidationAgent:
#     def __init__(self):
#         self.bank_api = BankAPI()

#     def verify_ownership(self, email: str, account_number: str) -> bool:
#         """Checks if the email matches the account owner in the DB."""
#         result = self.bank_api.ValidateAccountAPI(account_number)
#         if result["status"] == "VALID":
#             # In a real DB, you'd check if owner_email == sender_email
#             # For now, we simulate this check:
#             return True 
#         return False
    

from apis.bank_services import BankAPI
from utils.security import audit_log

class ValidationAgent:
    def __init__(self):
        self.bank_api = BankAPI()

    def verify_ownership(self, sender_email: str, account_number: str) -> bool:
        """
        SOLID: Logic remains deterministic. 
        Compares sender metadata with DB records.
        """
        if not sender_email or not account_number:
            audit_log("VALIDATION", "FAILED", "Missing sender or account info")
            return False

        # 1. Fetch the actual owner email from the DB
        result = self.bank_api.GetAccountOwnerEmail(account_number)
        
        if result["status"] == "SUCCESS":
            owner_email = result["email"].strip().lower()
            provided_email = sender_email.strip().lower()
            
            # 2. Strict Comparison
            if owner_email == provided_email:
                print(f"VERIFICATION SUCCESS: {provided_email} owns {account_number}")
                audit_log("VALIDATION", "SUCCESS", f"{provided_email} verified for {account_number}")
                return True
            else:
                print(f"SECURITY ALERT: {provided_email} attempted to access {account_number}")
                audit_log("VALIDATION", "ALERT", f"{provided_email} failed verification for {account_number}")
        else:
            audit_log("SECURITY", "FAILED", f"Account {account_number} not found in DB")

        return False