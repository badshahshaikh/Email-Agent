TABLES = {
    "customers": """
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """,
    "accounts": """
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(id),
            account_number TEXT UNIQUE NOT NULL,
            balance DECIMAL(15, 2) DEFAULT 0.00,
            account_type TEXT CHECK (account_type IN ('savings', 'checking')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """,
    "transactions": """
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            account_id INTEGER REFERENCES accounts(id),
            amount DECIMAL(15, 2) NOT NULL,
            description TEXT,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_credit_card BOOLEAN DEFAULT FALSE
        );
    """
}