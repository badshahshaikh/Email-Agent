# utils/formatter.py
import locale

def mask_number(number, visible_digits=4):
    """Turns 1234567890 into XXXX7890"""
    if not number: return "N/A"
    num_str = str(number)
    return "X" * (len(num_str) - visible_digits) + num_str[-visible_digits:]

def format_currency(amount):
    """Formats 125000 to INR 1,25,000"""
    # Simple manual format for INR style
    try:
        s, *d = str(amount).split(".")
        r = ",".join([s[max(i - 2, 0):i] for i in range(len(s) - 3, 0, -2)] + [s[-3:]])
        return f"INR {r}"
    except:
        return f"INR {amount}"