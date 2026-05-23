# apis/bank_services.py
import psycopg2
import os
import time
from decimal import Decimal
from config.db_pool import DatabasePool
from utils.security import audit_log
class BankAPI:

    def __init__(self):
        # We don't store a single connection; we use the pool context
        self.db = DatabasePool

    def GetAccountOwnerEmail(self, acc_num):
        """Fetches the registered email address for a specific account number."""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    # Join accounts with customers to get the email
                    query = """
                        SELECT c.email 
                        FROM accounts a 
                        JOIN customers c ON a.customer_id = c.id 
                        WHERE a.account_number = %s
                    """
                    cur.execute(query, (acc_num,))
                    result = cur.fetchone()
                    if result:
                        return {"status": "SUCCESS", "email": result[0]}
                    
                    audit_log("BANK_API", "INFO", f"GetAccountOwnerEmail called for {acc_num} - Result: {result}")
                    return {"status": "FAILED", "error": "Account not found"}
                    
                except Exception as e:
                    audit_log("BANK_API", "ERROR", f"GetAccountOwnerEmail failed for {acc_num} - Error: {str(e)}")
                    return {"status": "ERROR", "error": str(e)}
                    
                
    def ValidateAccountAPI(self, acc_num):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    query = "SELECT c.name FROM accounts a JOIN customers c ON a.customer_id = c.id WHERE a.account_number = %s"
                    cur.execute(query, (acc_num,))
                    result = cur.fetchone()
                    if result:
                        return {"status": "VALID", "customer_name": result[0]}
                    return {"status": "INVALID", "error": "Account not found"}
                except Exception as e:
                    return {"status": "ERROR", "error": str(e)}


    def ValidateCardAPI(self, card_num):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    query = "SELECT id FROM accounts WHERE account_number = %s"
                    cur.execute(query, (card_num,))
                    result = cur.fetchone() 
                    if result:
                        return {"status": "VALID", "card_number": card_num}
                    return {"status": "FAILED", "error": "Card not recognized"}
                except Exception as e:
                    return {"status": "ERROR", "error": str(e)}


    def GetAccountBalanceAPI(self, acc_num):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    query = "SELECT balance, account_type FROM accounts WHERE account_number = %s"
                    cur.execute(query, (acc_num,))
                    result = cur.fetchone()
                    if result:
                        return {"account": acc_num, "balance": float(result[0]), "type": result[1], "status": "SUCCESS"}
                    return {"status": "FAILED", "error": "Account not found"}
                except Exception as e:
                    return {"status": "ERROR", "error": str(e)}



    def GetCardTransactionsAPI(self, card_num, count=5):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    query = """
                        SELECT amount, description, transaction_date 
                        FROM transactions t
                        JOIN accounts a ON t.account_id = a.id
                        WHERE a.account_number = %s AND t.is_credit_card = TRUE
                        ORDER BY transaction_date DESC LIMIT %s
                    """
                    cur.execute(query, (card_num, count))
                    rows = cur.fetchall()
                    transactions = []
                    for r in rows:
                        transactions.append({
                            "amount": float(r[0]),
                            "description": r[1],
                            "date": r[2].strftime("%Y-%m-%d")
                        })
                        
                    return {
                        "card": f"XXXX-XXXX-XXXX-{card_num[-4:]}",
                        "transactions": transactions,
                        "status": "SUCCESS"
                    }
                except Exception as e:
                    return {"status": "ERROR", "error": str(e)}

    def GetStatementAPI(self, acc_num):

        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    query = """
                        SELECT amount, description, transaction_date 
                        FROM transactions t
                        JOIN accounts a ON t.account_id = a.id
                        WHERE a.account_number = %s
                        ORDER BY transaction_date DESC
                    """
                    cur.execute(query, (acc_num,))
                    rows = cur.fetchall()
                    
                    history = [{"amount": float(r[0]), "desc": r[1], "date": r[2].strftime("%Y-%m-%d")} for r in rows]
                    
                    return {
                        "account": acc_num,
                        "transactions": history,
                        "status": "SUCCESS",
                        "total_records": len(history),
                        "document": f"STMT-{acc_num[-4:]}-{int(time.time())}"
                    }
                except Exception as e:
                    return {"status": "ERROR", "error": str(e)}
                
