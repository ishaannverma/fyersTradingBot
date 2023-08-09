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
    redirect_uri='http://127.0.0.1:5000/login/redirecturi',
    response_type='code',
    grant_type='authorization_code'
)

from flask import Blueprint, request, redirect, url_for
import webbrowser

from modules.logging import Logger
from modules.templates import LogLevel


class Model:
    model = None

    def setModel(self, newmodel):
        self.model = newmodel

    def checkValidityofModel(self, logger, tokenTime):
        timeDiff = datetime.now() - tokenTime
        if timeDiff > timedelta(hours=14):
            logger.add_log(LogType.INFO,
                           f"Autologin failed: timestamp too old: {int(timeDiff.total_seconds() / 3600)} hours")
            return False
        else:
            logger.add_log(LogType.INFO, f"Saved token found: {int(timeDiff.total_seconds() / 3600)} hours old")

        try:
            response = self.model.get_profile()
            if response['code'] == 200:
                return True
            else:
                logger.add_log(LogType.INFO, f"Autologin failed: {response['message']}")
        except Exception as e:
            logger.add_log(LogType.ERROR, f"Couldn't autologin: {e}")

        return False

    def checkConnection(self, logger):
        response = None
        try:
            response = self.model.get_profile()
        except Exception as e:
            logger.add_log(LogType.FATAL, f"Problem connecting: {e}")

        if response['code'] == 200:
            logger.add_log(LogType.INFO, "Connection Verified!")
            return True
        else:
            logger.add_log(LogType.FATAL, f"Problem connecting: {response['s']}")

        return False


fyers_model = Model()
logger = Logger(LogLevel.DEBUG)
login_blueprint = Blueprint('login', __name__, static_folder='static', template_folder='templates',
                            url_prefix='/login')


@login_blueprint.route('starter')
def loginStarter(logger=logger, autoLogin: bool = True):
    # todo add a success handler
    # check if already exists
    if os.path.exists(loginLogLocation) and autoLogin:
        with open(loginLogLocation, 'r') as f:
            try:
                loginText = f.read().split()
                tokenTime = datetime.fromtimestamp(int(loginText[0]))
                token = loginText[1]

                app_credentials['ACCESS_TOKEN'] = token
                app_credentials['WS_ACCESS_TOKEN'] = f"{app_credentials['APP_ID']}:{app_credentials['ACCESS_TOKEN']}"

                newmodel = fyersModel.FyersModel(client_id=app_credentials['APP_ID'],
                                              token=app_credentials['ACCESS_TOKEN'],
                                              log_path=logger.logging_path)
                fyers_model.setModel(newmodel)
                if fyers_model.checkValidityofModel(logger, tokenTime):
                    logger.add_log(LogType.INFO, "Auto Login through saved credentials successful!")
                    return redirect(url_for('index'))
            except Exception as e:
                logger.add_log(LogType.ERROR, e)

    return redirect(url_for('.login'))


@login_blueprint.route('generateurl')
def login(logger=logger):
    # TODO front landing page if autologin

    # if not, make new model
    # Step 1
    logger.add_log(LogType.INFO, "Logging in manually")
    response = session.generate_authcode()
    return redirect(response)
    # webbrowser.open_new(response)

    # return "You would be redirected to another tab. You can close this now."


@login_blueprint.route('redirecturi')
def redirecturi():
    auth_code = request.args.get('auth_code')
    session.set_token(auth_code)
    response = session.generate_token()

    app_credentials['ACCESS_TOKEN'] = response['access_token']
    app_credentials['WS_ACCESS_TOKEN'] = f"{app_credentials['APP_ID']}:{app_credentials['ACCESS_TOKEN']}"

    # save this token
    with open(loginLogLocation, 'w') as f:
        f.write(f"{int(datetime.now().timestamp())} {app_credentials['ACCESS_TOKEN']}")

    newmodel = fyersModel.FyersModel(client_id=app_credentials['APP_ID'], token=app_credentials['ACCESS_TOKEN'],
                                        log_path=logger.logging_path)

    fyers_model.setModel(newmodel)

    if fyers_model.checkConnection(logger):
        logger.add_log(LogType.INFO, "Login through redirection successful!")
    return redirect(url_for('index'))
