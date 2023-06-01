import os
from dotenv import load_dotenv
import requests

load_dotenv()


def get_tokens():
    login = os.getenv('LOGIN')
    password = os.getenv('PASSWORD')
    client_id = os.getenv('CLIENT_ID')
    secret_code = os.getenv('secret_code')
    params = {'login': login,
              'password': password,
              'client_id': client_id,
              'client_secret': secret_code
              }
    response = requests.post('https://api.superjob.ru/2.0/oauth2/password/', params=params)
    print(response.json())

if __name__ == '__main__':
    get_tokens()
