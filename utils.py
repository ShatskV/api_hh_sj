import os
from dotenv import load_dotenv
import requests

def get_tokens_sj():
    login = os.getenv('SJ_LOGIN')
    password = os.getenv('SJ_PASSWORD')
    client_id = os.getenv('SJ_CLIENT_ID')
    secret_code = os.getenv('SJ_SECRET_CODE')
    params = {'login': login,
              'password': password,
              'client_id': client_id,
              'client_secret': secret_code
              }
    response = requests.post('https://api.superjob.ru/2.0/oauth2/password/', params=params)
    print(response.json())

if __name__ == '__main__':
    load_dotenv()
    get_tokens_sj()
