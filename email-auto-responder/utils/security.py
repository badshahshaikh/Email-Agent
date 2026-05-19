# utils/security.py
import logging

# Configure Logging to file
logging.basicConfig(filename='logs/audit.log', level=logging.INFO)

def mask_data(data):
    """Masks account and card numbers for logs"""
    if isinstance(data, str) and len(data) > 4:
        return "*" * (len(data) - 4) + data[-4:]
    return data

def audit_log(customer_name, intent, status):
    logging.info(f"Customer: {customer_name} | Action: {intent} | Status: {status}")