# config/db_pool.py
import os
import psycopg2.pool
from contextlib import contextmanager

class DatabasePool:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            print("Initializing ThreadedConnectionPool...")
            cls._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.getenv("DB_HOST", "127.0.0.1"),
                database=os.getenv("DB_NAME", "bank_db"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASS", "postgres")
            )
        return cls._pool

    @classmethod
    def close_all(cls):
        if cls._pool:
            cls._pool.closeall()
            print("Connection pool closed.")

    @classmethod
    @contextmanager
    def get_connection(cls):
        """Context manager to borrow and return connections safely"""
        pool = cls.get_pool()
        conn = pool.getconn()
        try:
            yield conn
        finally:
            pool.putconn(conn)