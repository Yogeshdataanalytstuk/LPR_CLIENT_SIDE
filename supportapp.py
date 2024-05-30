import requests

def send_plate():
    try:
        # Authenticate and get a session token if necessary
        session = requests.Session()

        # If authentication is required
        login_url = 'http://127.0.0.1:5000/login'
        login_data = {'username': 'nds', 'password': 'nds'}
        response = session.post(login_url, data=login_data)

        if response.status_code == 200:
            print("Logged in successfully")
        else:
            print("Failed to log in. Status code:", response.status_code)
            return

        while True:
            # Get user input for the number plate
            plate = input("Enter the number plate (or 'exit' to stop): ").upper()
            if plate.lower() == 'exit':
                break

            url = 'http://127.0.0.1:5000/submit_plate'
            data = {'plate': plate}
            
            # Sending the POST request to the Flask server
            response = session.post(url, json=data)

            # Check if the request was successful
            if response.status_code == 200:
                print("Response from server:", response.text)
            else:
                print("Failed to send plate. Status code:", response.status_code)
                print("Error message:", response.text)

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    send_plate()
