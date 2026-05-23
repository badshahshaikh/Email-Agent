# utils/db_seeder.py
import psycopg2
import os
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        database=os.getenv("DB_NAME", "bank_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "postgres_password"), # Replace with your real password
    )

def seed_database(conn=None):
    if conn is None:
        conn = get_connection()
    conn.autocommit = False # We use manual transactions for safety
    cur = conn.cursor()

    try:
        print("🌱 Starting Database Seeding...")

        # --- 1. SEED CUSTOMERS ---
        customer_ids = []
        for _ in range(5): # Create 5 customers
            name = fake.name()
            email = fake.email()
            # Idempotency: ON CONFLICT DO NOTHING
            cur.execute("""
                INSERT INTO customers (name, email) VALUES (%s, %s) 
                ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
                RETURNING id;
            """, (name, email))
            customer_ids.append(cur.fetchone()[0])
        
        print(f"✅ Seeded {len(customer_ids)} customers.")

        # --- 2. SEED ACCOUNTS ---
        account_ids = []
        # Predefined account for testing consistency
        test_accounts = [
            (customer_ids[0], '1234567890', 5000.00, 'savings'),
            (customer_ids[1], '9876543210', 1200.50, 'checking')
        ]
        
        for cust_id, acc_num, bal, acc_type in test_accounts:
            cur.execute("""
                INSERT INTO accounts (customer_id, account_number, balance, account_type) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT (account_number) DO UPDATE SET balance = EXCLUDED.balance
                RETURNING id;
            """, (cust_id, acc_num, bal, acc_type))
            account_ids.append(cur.fetchone()[0])
            
        print(f"✅ Seeded {len(account_ids)} bank accounts.")

        # --- 3. SEED TRANSACTIONS ---
        # Generate 20 random transactions
        for _ in range(20):
            acc_id = random.choice(account_ids)
            amount = random.uniform(-200.0, 500.0) # Mix of deposits and withdrawals
            is_cc = random.choice([True, False])
            desc = fake.sentence(nb_words=3)
            # Realistic timestamp within last 30 days
            date = datetime.now() - timedelta(days=random.randint(0, 30))

            cur.execute("""
                INSERT INTO transactions (account_id, amount, description, transaction_date, is_credit_card)
                VALUES (%s, %s, %s, %s, %s)
            """, (acc_id, amount, desc, date, is_cc))

        conn.commit()
        print("✅ Seeded 20 transactions.")
        print("🚀 Seeding Complete!")

    except Exception as e:
        conn.rollback()
        print(f"❌ Seeding Failed: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_database()