# utils/db_initializer.py
import psycopg2
import os
import time
from models.schema import TABLES
from dotenv import load_dotenv
load_dotenv()

# def initialize_database():
#     db_host = os.getenv("DB_HOST", "localhost")
#     db_name = os.getenv("DB_NAME", "db_name")
#     db_user = os.getenv("DB_USER", "postgres_user")
#     db_pass = os.getenv("DB_PASS", "postgres_password")

#     conn = None
#     max_retries = 5
    
#     print(f"Connecting to PostgreSQL at {db_host}...")
    
#     for i in range(max_retries):
#         try:
#             # 1. Connect to default 'postgres' to check if DB exists
#             conn = psycopg2.connect(
#                 host=db_host, 
#                 user=db_user, 
#                 password=db_pass, 
#                 dbname=db_name,
#                 port="5432"
#             )
#             conn.autocommit = True
#             cur = conn.cursor()
            
#             # 2. Create the bank_db if it doesn't exist
#             cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
#             exists = cur.fetchone()
#             if not exists:
#                 cur.execute(f"CREATE DATABASE {db_name}")
#                 print(f"Database {db_name} created successfully.")
            
#             cur.close()
#             conn.close()

#             # 3. Connect to the actual bank_db to create tables
#             conn = psycopg2.connect(
#                 host=db_host, 
#                 user=db_user, 
#                 password=db_pass, 
#                 dbname=db_name,
#                 port="5432"
#             )
#             cur = conn.cursor()
            
#             for table_name, query in TABLES.items():
#                 cur.execute(query)
#                 print(f"Table '{table_name}' verified/created.")
            
#             conn.commit()
#             print("✅ Database initialization complete.")
#             break

#         except psycopg2.OperationalError as e:
#             print(f"❌ Connection failed (Attempt {i+1}/{max_retries}). Retrying...")
#             time.sleep(3)
#         finally:
#             if conn:
#                 cur.close()
#                 conn.close()
#     else:
#         print("🚨 CRITICAL: Could not connect to PostgreSQL. Is it installed and running?")

# utils/db_initializer.py
import psycopg2
import os
import time
from models.schema import TABLES

def initialize_database():
    # 1. HARDCODE THESE for testing to ensure environment variables aren't the problem
    db_host = "127.0.0.1"  # Use IP instead of 'localhost'
    db_user = "postgres"
    db_pass = "postgres" # Use the password you typed in psql
    db_name = "bank_db"

    conn = None
    print(f"Connecting to PostgreSQL at {db_host}...")
    
    try:
        # Step A: Connect to default 'postgres' database first
        conn = psycopg2.connect(
            host=db_host, 
            user=db_user, 
            password=db_pass, 
            dbname="postgres",
            port="5432"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Step B: Create bank_db if it doesn't exist
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"Database {db_name} created.")
        
        cur.close()
        conn.close()

        # Step C: Connect to actual bank_db and create tables
        conn = psycopg2.connect(
            host=db_host, 
            user=db_user, 
            password=db_pass, 
            dbname=db_name,
            port="5432"
        )
        cur = conn.cursor()
        for table_name, query in TABLES.items():
            cur.execute(query)
        
        conn.commit()
        print("✅ Database initialization complete.")

    except Exception as e:
        # This will tell us the REAL reason (Wrong password? Wrong port?)
        print(f"🚨 DATABASE ERROR: {e}")
    finally:
        if conn:
            conn.close()