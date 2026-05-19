# apis/bank_services.py
import psycopg2
import os
import time
from decimal import Decimal

class BankAPI:
    @staticmethod
    def _get_connection():
        """Helper to create a fresh DB connection"""
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            database=os.getenv("DB_NAME", "bank_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", "postgres_password"), # Replace with your real password
            connect_timeout=5,
            options="-c statement_timeout=5000" 
        )

    @staticmethod
    def ValidateAccountAPI(acc_num):
        """Query accounts and customers table to validate existence"""
        conn = None
        try:
            conn = BankAPI._get_connection()
            cur = conn.cursor()
            
            # Join accounts with customers to get the owner's name
            query = """
                SELECT c.name FROM accounts a 
                JOIN customers c ON a.customer_id = c.id 
                WHERE a.account_number = %s
            """
            cur.execute(query, (acc_num,))
            result = cur.fetchone()
            
            if result:
                return {"status": "VALID", "customer_name": result[0]}
            return {"status": "INVALID", "error": "Account number not found"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
        finally:
            if conn: conn.close()

    @staticmethod
    def ValidateCardAPI(card_num):
        """Verify if the card number (mapped to account) exists"""
        conn = None
        try:
            conn = BankAPI._get_connection()
            cur = conn.cursor()
            
            # In our schema, card transactions are linked to accounts
            # We validate if the account exists for this card number
            query = "SELECT id FROM accounts WHERE account_number = %s"
            cur.execute(query, (card_num,))
            if cur.fetchone():
                return {"status": "VALID", "card_number": card_num}
            return {"status": "INVALID", "error": "Card not recognized"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
        finally:
            if conn: conn.close()

    @staticmethod
    def GetAccountBalanceAPI(acc_num):
        """Query accounts table for current balance"""
        conn = None
        try:
            conn = BankAPI._get_connection()
            cur = conn.cursor()
            
            query = "SELECT balance, account_type FROM accounts WHERE account_number = %s"
            cur.execute(query, (acc_num,))
            result = cur.fetchone()
            
            if result:
                # Convert Decimal to float for JSON compatibility
                return {
                    "account": acc_num, 
                    "balance": float(result[0]), 
                    "type": result[1], 
                    "status": "SUCCESS"
                }
            return {"status": "FAILED", "error": "Account not found"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
        finally:
            if conn: conn.close()

    @staticmethod
    def GetCardTransactionsAPI(card_num, count=5):
        """Query transactions table where is_credit_card = TRUE"""
        conn = None
        try:
            conn = BankAPI._get_connection()
            cur = conn.cursor()
            
            # Find transactions linked to the account with credit card flag
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
        finally:
            if conn: conn.close()

    @staticmethod
    def GetStatementAPI(acc_num):
        """Query all transactions for the account (History)"""
        conn = None
        try:
            conn = BankAPI._get_connection()
            cur = conn.cursor()
            
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
                "total_records": len(history)
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
        finally:
            if conn: conn.close()