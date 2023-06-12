import sys

from fyers_api import accessToken
from fyers_api import fyersModel
from urllib.parse import urlparse
from datetime import datetime, timedelta
from modules.keys import credentials
import os

loginLogLocation = os.path.join(os.getcwd(), 'logs', 'login.txt')

session = accessToken.SessionModel(
    client_id=credentials['APP_ID'],
    secret_key=credentials['SECRET_ID'],
    redirect_uri='http://127.0.0.1:5000/login',
    response_type='code',
    grant_type='authorization_code'
)


def checkValidityofModel(fyers, tokenTime):
    timeDiff = datetime.now() - tokenTime
    if timeDiff > timedelta(hours=14):
        print(f"Autologin failed: timestamp too old: {int(timeDiff.total_seconds() / 3600)} hours")
        return False
    else:
        print(f"Saved token found: {int(timeDiff.total_seconds() / 3600)} hours old")

    try:
        response = fyers.get_profile()
        if response['code'] == 200:
            return True
        else:
            print(f"Autologin failed: {response['message']}")
    except Exception as e:
        print(f"Couldn't autologin: {e}")
        pass

    return False


def checkConnection(fyers) -> [bool, str]:
    response = None
    try:
        response = fyers.get_profile()
    except Exception as e:
        sys.exit(f"Problem connecting: {e}")

    if response['code'] == 200:
        print("Connection Verified!")
    else:
        sys.exit(f"Problem connecting: {response['s']}")


def login(logger, autoLogin: bool = True):
    # check if already exists
    if os.path.exists(loginLogLocation) and autoLogin:
        with open(loginLogLocation, 'r') as f:
            try:
                loginText = f.read().split()
                tokenTime = datetime.fromtimestamp(int(loginText[0]))
                token = loginText[1]
            except Exception as e:
                print(e)
            credentials['ACCESS_TOKEN'] = token
            credentials['WS_ACCESS_TOKEN'] = f"{credentials['APP_ID']}:{credentials['ACCESS_TOKEN']}"
            fyers = fyersModel.FyersModel(client_id=credentials['APP_ID'], token=credentials['ACCESS_TOKEN'],
                                          log_path=logger.path)
            if checkValidityofModel(fyers, tokenTime):
                print("INFO: Auto Login Successful!")
                return fyers
    # TODO front landing page if autologin

    # if not, make new model
    # Step 1
    print("INFO: Logging in manually")
    response = session.generate_authcode()
    print(response)

    # Step 2
    redirect_uri = input("Redirect URI: ")
    t = urlparse(redirect_uri)
    auth_code = dict([x.split('=') for x in t.query.split('&')])['auth_code']
    session.set_token(auth_code)
    response = session.generate_token()

    credentials['ACCESS_TOKEN'] = response['access_token']
    credentials['WS_ACCESS_TOKEN'] = f"{credentials['APP_ID']}:{credentials['ACCESS_TOKEN']}"

    # save this token
    with open(loginLogLocation, 'w') as f:
        f.write(f"{int(datetime.now().timestamp())} {credentials['ACCESS_TOKEN']}")

    return fyersModel.FyersModel(client_id=credentials['APP_ID'], token=credentials['ACCESS_TOKEN'],
                                 log_path=logger.path)
