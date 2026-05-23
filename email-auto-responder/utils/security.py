# utils/security.py
import logging
import inspect
import os

# Configure Logging to file
logging.basicConfig(
    filename='logs/audit.log', 
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)


def mask_data(data):
    """Masks account and card numbers for logs"""
    if isinstance(data, str) and len(data) > 4:
        return "*" * (len(data) - 4) + data[-4:]
    return data

def audit_log(event_type, status, details):
    """
    event_type: INBOUND_EMAIL, API_CALL, SMTP_SEND
    status: SUCCESS, FAILED, PENDING
    details: Dict or String
    """
    # logging.info(f"EVENT: {event_type} | STATUS: {status} | DATA: {details}")

    caller_frame = inspect.stack()[1]
    filename = os.path.basename(caller_frame.filename)
    line_number = caller_frame.lineno
    function_name = caller_frame.function

    log_message = (
        f"SOURCE: {filename}:{line_number} ({function_name}) | "
        f"EVENT: {event_type} | STATUS: {status} | DATA: {details}"
    )
    
    logging.info(log_message)
