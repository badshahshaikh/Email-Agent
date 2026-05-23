# utils/db_initializer.py
import psycopg2
import os
import time
from models.schema import TABLES
from dotenv import load_dotenv
from .db_seeder import seed_database
load_dotenv()

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
        print("Checking if seeding is required...")
        seed_database(conn)


    except Exception as e:
        # This will tell us the REAL reason (Wrong password? Wrong port?)
        print(f"🚨 DATABASE ERROR: {e}")
    finally:
        if conn:
            conn.close()