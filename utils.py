import requests
from pprint import pprint
import json

import random
import string

st = string.ascii_letters

def create_account(userName: str, email: str, password: str, country="ca"):
    session = requests.Session()
    headers = {
        "authority": "spclient.wg.spotify.com",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36",
        "accept": "*/*",
        "origin": "https://www.spotify.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.spotify.com/",
        "accept-language": "en-US,en;q=0.9",
    }
    r = session.get(f"https://www.spotify.com/{country}-en/signup", headers=headers)
    cookies = r.cookies
    data = {
        "account_details": {
            "birthdate": "1995-05-05",
            "consent_flags": {
                "eula_agreed": "true",
                "send_email": "true",
                "third_party_email": "true",
            },
            "display_name": userName,
            "email_and_password_identifier": {"email": email, "password": password},
            "gender": 1,
        },
        "callback_uri": f"https://www.spotify.com/signup/challenge?forward_url=https%3A%2F%2Fopen.spotify.com%2F&locale={country}-en",
        "client_info": {
            "api_key": "a1e486e2729f46d6bb368d6b2bcda326",
            "app_version": "v2",
            "capabilities": [2],
            "installation_id": "db279054-bffd-4fa0-a993-227dda4b6bc3",
            "platform": "www",
        },
        "tracking": {
            "creation_flow": "",
            "creation_point": f"https://www.spotify.com/{country}-en/",
            "referrer": "",
        },
    }

    data = json.dumps(data)

    response = session.post(
        "https://spclient.wg.spotify.com/signup/public/v2/account/create",
        headers=headers,
        data=data,
        cookies=cookies,
    )

    if response.status_code == 200:
        print("SUCCESS!")
        return response.json(), True
    else:
        print("FAILURE!")
        return response.json()["error"]["error_details"], False


r = create_account("FUSZ", "testwdadwer@promail.com", "12345wadawdad6")
print(r)