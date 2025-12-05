import requests
import time
import sys

def check_health():
    url = "http://localhost:5001/health"
    for i in range(10):
        try:
            print(f"Attempt {i+1} connecting to {url}...")
            response = requests.get(url)
            if response.status_code == 200:
                print("Health check passed!")
                print(response.json())
                return True
        except requests.exceptions.ConnectionError:
            print("Connection failed, retrying in 2s...")
            time.sleep(2)
    return False

if __name__ == "__main__":
    if not check_health():
        sys.exit(1)
