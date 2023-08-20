from fyers_api import accessToken
from modules.login.fyersmodel import Model
from fyers_api import fyersModel

from datetime import datetime
from modules.keys import app_credentials
import os

loginLogLocation = os.path.join(os.getcwd(), 'logs', 'login.txt')

session = accessToken.SessionModel(
    client_id=app_credentials['APP_ID'],
    secret_key=app_credentials['SECRET_ID'],
    redirect_uri='http://127.0.0.1:5000/login/redirecturi',
    response_type='code',
    grant_type='authorization_code'
)

from flask import Blueprint, request, redirect, url_for
from modules.logging.logging import loggerObject as logger
from modules.logic.templates import LogType

fyers_model_class_obj = Model()
login_blueprint = Blueprint('login', __name__, static_folder='modules/login/static',
                            template_folder='modules/login/templates',
                            url_prefix='/login')


@login_blueprint.route('starter')
def loginStarter(logger=logger, autoLogin: bool = True):
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
                fyers_model_class_obj.setModel(newmodel)
                if fyers_model_class_obj.checkValidityofModel(tokenTime, logger):
                    logger.add_log(LogType.INFO, "Auto Login through saved credentials successful!")
                    return redirect(url_for('index'))
            except Exception as e:
                logger.add_log(LogType.ERROR, e)

    return redirect(url_for('.login'))


@login_blueprint.route('generateurl')
def login(logger=logger):

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

    fyers_model_class_obj.setModel(newmodel)

    if fyers_model_class_obj.checkConnection(logger):
        logger.add_log(LogType.INFO, "Login through redirection successful!")
    return redirect(url_for('index'))
