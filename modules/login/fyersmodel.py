from fyers_api import accessToken
from datetime import datetime, timedelta
from modules.keys import app_credentials
import os
from modules.logic.templates import LogType

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
    model = None

    def setModel(self, newmodel):
        self.model = newmodel

    def checkValidityofModel(self, tokenTime, logger=logger):
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

    def checkConnection(self, logger=logger):
        response = None
        try:
            response = self.model.get_profile()
        except Exception as e:
            logger.add_log(LogType.ERROR, f"Problem connecting: {e}")
            return False

        if response['code'] == 200:
            logger.add_log(LogType.INFO, "Connection Verified!")
            return response['data']['fy_id']
        else:
            logger.add_log(LogType.ERROR, f"Problem connecting: {response['s']}")

        return False



