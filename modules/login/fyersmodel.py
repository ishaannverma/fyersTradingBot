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
    _model = None

    def setModel(self, newmodel):
        self._model = newmodel

    def checkValidityofModel(self, tokenTime, logger=logger):
        timeDiff = datetime.now() - tokenTime
        if timeDiff > timedelta(hours=14):
            logger.add_log(LogType.INFO,
                           f"Autologin failed: timestamp too old: {int(timeDiff.total_seconds() / 3600)} hours")
            return False
        else:
            logger.add_log(LogType.INFO, f"Saved token found: {int(timeDiff.total_seconds() / 3600)} hours old")

        try:
            response = self._model.get_profile()
            if response['code'] == 200:
                return True
            else:
                logger.add_log(LogType.INFO, f"Autologin failed: {response['message']}")
        except Exception as e:
            logger.add_log(LogType.ERROR, f"Couldn't autologin: {e}")

        return False

    def checkConnection(self, logger=logger):
        response = None
        if self._model is None:
            return False
        try:
            response = self.getModel().get_profile()
        except Exception as e:
            logger.add_log(LogType.DEBUG, f"Problem connecting: {e}")
            return False

        if response['code'] == 200:
            logger.add_log(LogType.DEBUG, "Connection Verified!")
            return True
        else:
            logger.add_log(LogType.DEBUG, f"Problem connecting: {response['s']}")

        return False

    def getModel(self):
        return self._model
        # if self.checkConnection(logger):
        #     return self._model
        # else:
        #     return "Problem with getModel(), please reload"
