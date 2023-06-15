import sys

from fyers_api import accessToken
from fyers_api import fyersModel
from urllib.parse import urlparse
from datetime import datetime, timedelta
from modules.keys import app_credentials
import os
from modules.templates import LogType

loginLogLocation = os.path.join(os.getcwd(), 'logs', 'login.txt')

session = accessToken.SessionModel(
    client_id=app_credentials['APP_ID'],
    secret_key=app_credentials['SECRET_ID'],
    redirect_uri='http://127.0.0.1:5000/login',
    response_type='code',
    grant_type='authorization_code'
)


def checkValidityofModel(fyers, logger, tokenTime):
    timeDiff = datetime.now() - tokenTime
    if timeDiff > timedelta(hours=14):
        logger.add_log(LogType.PRINT,
                       f"Autologin failed: timestamp too old: {int(timeDiff.total_seconds() / 3600)} hours")
        return False
    else:
        logger.add_log(LogType.PRINT, f"Saved token found: {int(timeDiff.total_seconds() / 3600)} hours old")

    try:
        response = fyers.get_profile()
        if response['code'] == 200:
            return True
        else:
            logger.add_log(LogType.PRINT, f"Autologin failed: {response['message']}")
    except Exception as e:
        logger.add_log(LogType.PRINT, f"Couldn't autologin: {e}")
        pass

    return False


def checkConnection(fyers, logger):
    response = None
    try:
        response = fyers.get_profile()
    except Exception as e:
        logger.add_log(LogType.FATAL, f"Problem connecting: {e}")

    if response['code'] == 200:
        logger.add_log(LogType.INFO, "Connection Verified!")
    else:
        logger.add_log(LogType.FATAL, f"Problem connecting: {response['s']}")


def login(logger, autoLogin: bool = True):
    # check if already exists
    if os.path.exists(loginLogLocation) and autoLogin:
        with open(loginLogLocation, 'r') as f:
            try:
                loginText = f.read().split()
                tokenTime = datetime.fromtimestamp(int(loginText[0]))
                token = loginText[1]
            except Exception as e:
                logger.add_log(LogType.ERROR, e)
            app_credentials['ACCESS_TOKEN'] = token
            app_credentials['WS_ACCESS_TOKEN'] = f"{app_credentials['APP_ID']}:{app_credentials['ACCESS_TOKEN']}"
            fyers = fyersModel.FyersModel(client_id=app_credentials['APP_ID'], token=app_credentials['ACCESS_TOKEN'],
                                          log_path=logger.path)
            if checkValidityofModel(fyers, logger, tokenTime):
                logger.add_log(LogType.INFO, "Auto Login Successful!")
                return fyers
    # TODO front landing page if autologin

    # if not, make new model
    # Step 1
    logger.add_log(LogType.INFO, "Logging in manually")
    response = session.generate_authcode()
    print(response)

    # Step 2
    redirect_uri = input("Redirect URI: ")
    t = urlparse(redirect_uri)
    auth_code = dict([x.split('=') for x in t.query.split('&')])['auth_code']
    session.set_token(auth_code)
    response = session.generate_token()

    app_credentials['ACCESS_TOKEN'] = response['access_token']
    app_credentials['WS_ACCESS_TOKEN'] = f"{app_credentials['APP_ID']}:{app_credentials['ACCESS_TOKEN']}"

    # save this token
    with open(loginLogLocation, 'w') as f:
        f.write(f"{int(datetime.now().timestamp())} {app_credentials['ACCESS_TOKEN']}")

    return fyersModel.FyersModel(client_id=app_credentials['APP_ID'], token=app_credentials['ACCESS_TOKEN'],
                                 log_path=logger.path)
