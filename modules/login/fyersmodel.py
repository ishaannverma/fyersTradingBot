from fyers_api import accessToken
from datetime import datetime, timedelta
from modules.keys import app_credentials
import os
from modules.logic.templates import LogType
from flask import url_for, redirect

loginLogLocation = os.path.join(os.getcwd(), 'logs', 'login.txt')

session = accessToken.SessionModel(
    client_id=app_credentials['APP_ID'],
    secret_key=app_credentials['SECRET_ID'],
    redirect_uri='http://127.0.0.1:5000/login/redirecturi',
    response_type='code',
    grant_type='authorization_code'
)

from modules.logging.logging import loggerObject as logger


class Model:

    def __init__(self):
        self._model = None
        self._WS_ACCESS_TOKEN = None

    ########################### MODEL METHODS ###########################

    def model_exists(self):
        if self._model is None:
            return False
        return True

    def setModel(self, newmodel, websocket_access_token):
        self._model = newmodel
        self._WS_ACCESS_TOKEN = websocket_access_token

    def get_WS_Access_token(self):
        return self._WS_ACCESS_TOKEN

    def checkValidityofModel(self, tokenTime, logger=logger):
        if not self.model_exists():
            return False

        timeDiff = datetime.now() - tokenTime
        if timeDiff > timedelta(hours=14):
            logger.add_log(LogType.INFO,
                           f"Autologin failed: timestamp too old: {int(timeDiff.total_seconds() / 3600)} hours")
            return False
        else:
            logger.add_log(LogType.INFO, f"Saved token found: {int(timeDiff.total_seconds() / 3600)} hours old")

            status, response = self.get_profile()
            if status is True:
                if response['code'] == 200:
                    return True
                else:
                    logger.add_log(LogType.INFO, f"Autologin failed: {response['message']}")
            else:
                logger.add_log(LogType.INFO, f"Autologin failed: {response['message']}")

        return False

    def checkConnection(self, logger=logger):
        if not self.model_exists():
            return False

        status, response = self.get_profile()

        if status is False:
            logger.add_log(LogType.DEBUG, f"Failure to verify connection: {response}")
            return False

        if response['code'] == 200:
            logger.add_log(LogType.DEBUG, "Connection Verified!")
            return True
        else:
            logger.add_log(LogType.DEBUG, f"Failure to verify connection: {response['s']}")

        return False

    ########################### DEFINE WRAPPER FUNCTIONS ###########################

    def get_profile(self):
        # if status is false, return_value will have error msg
        if not self.model_exists():
            return False, "Model doesn't exist/ not set up yet"

        try:
            rsp = self._model.get_profile()
            if rsp['code'] == 200:
                status = True
                return_value = rsp
            else:
                status = False
                return_value = rsp['message']
        except Exception as e:
            status = False
            return_value = e

        return status, return_value

    def funds(self):
        # if status is false, return_value will have error msg
        if not self.model_exists():
            return False, "Model doesn't exist/ not set up yet"

        try:
            rsp = self._model.funds()
            if rsp['code'] == 200:
                status = True
                return_value = rsp
            else:
                status = False
                return_value = rsp['msg']
        except Exception as e:
            status = False
            return_value = e

        return status, return_value

    def positions(self):
        # if status is false, return_value will have error msg
        if not self.model_exists():
            return False, "Model doesn't exist/ not set up yet"

        try:
            rsp = self._model.positions()
            if rsp['code'] == 200:
                status = True
                return_value = rsp
            else:
                status = False
                return_value = rsp['msg']
        except Exception as e:
            status = False
            return_value = e

        return status, return_value

    def place_order(self, order_data):
        # if status is false, return_value will have error msg
        if not self.model_exists():
            return False, "Model doesn't exist/ not set up yet"

        try:
            rsp = self._model.place_order(order_data)
            if rsp['code'] == 200:
                status = True
                return_value = rsp
            else:
                status = False
                return_value = rsp['msg']
        except Exception as e:
            status = False
            return_value = e

        return status, return_value

    def quotes(self, quotes_data):
        # if status is false, return_value will have error msg
        if not self.model_exists():
            return False, "Model doesn't exist/ not set up yet"

        try:
            rsp = self._model.quotes(quotes_data)
            if rsp['code'] == 200:
                status = True
                return_value = rsp
            else:
                status = False
                return_value = rsp['msg']
        except Exception as e:
            status = False
            return_value = e

        return status, return_value

