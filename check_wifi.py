import requests

def is_internet_available():
    try:
        # Send a simple HTTP GET request to a reliable server (e.g., Google)
        print("\tSending Wifi Check request...")
        response = requests.get("https://www.google.com", timeout=5)
        # If the request is successful (status code 200), return True
        return response.status_code == 200
    except requests.ConnectionError:
        # If there is a connection error (e.g., no internet), return False
        return False



def is_internet_availableTwo():
    try:
        # Send a simple HTTP GET request to a reliable server (e.g., Google)
        #print("\tSending Wifi Check request...")
        response = requests.get("https://www.google.com", timeout=5)
        # If the request is successful (status code 200), return True
        return response.status_code == 200
    except requests.ConnectionError:
        # If there is a connection error (e.g., no internet), return False
        return False

