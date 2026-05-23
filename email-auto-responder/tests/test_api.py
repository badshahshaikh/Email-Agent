# test_api.py
import requests
import json
import time

API_URL = "http://127.0.0.1:8001/process-email"

def run_test(name, body, sender):
    print(f"\n{'='*50}")
    print(f"RUNNING TEST: {name}")
    print(f"Sender: {sender}")
    print(f"Body: {body}")
    print(f"{'='*50}")

    payload = {
        "body": body,
        "sender": sender
    }

    start_time = time.time()
    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        duration = time.time() - start_time
        
        print(f"Time Taken: {duration:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("SERVER ERROR DETECTED:")
            print(response.text)

    except Exception as e:
        print(f"CONNECTION ERROR: {str(e)}")

if __name__ == "__main__":
    # SCENARIO 1: Valid Ownership (Should succeed if DB matches)
    # Ensure this email and account exist in your DB together!
    run_test(
        "VALID BALANCE CHECK",
        "Hi, what is my balance for account 1234567890?",
        "officialbadshahyou2@gmail.com"
    )

    # SCENARIO 2: Email Mismatch (Should fail Security Validation)
    run_test(
        "SECURITY TEST (EMAIL MISMATCH)",
        "Please send the statement for account 1234567890",
        "hacker@gmail.com"
    )

    # SCENARIO 3: Multi-Intent
    run_test(
        "MULTI-INTENT TEST",
        "Give me my balance for 1234567890 and also last 5 transactions for card 9876543210",
        "officialbadshahyou2@gmail.com"
    )