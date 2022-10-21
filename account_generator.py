from utils import create_account
import random




if __name__ == "__main__":
    emails = [
        {
            "email": "freespo333nonet.net",
            "password": "password123"
        },
        {
            "email": "freespo333nonet.net",
            "password": "password123"
        }
    ]
    for email in emails:
        resp, done = create_account("Undefined", email["email"], email["password"])
        if done:
            print("Success!", email["email"], email["password"])
        else:
            print("Failed to create", email["email"], email["password"])
            
