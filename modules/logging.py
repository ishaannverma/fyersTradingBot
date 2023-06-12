import os
from modules.telegram import sendTelegram

class logger:
    path = ""
    log_type = {
        'INFO',
        'DEBUG',
        'WARNING',
        'ERROR'
    }

    def __init__(self):
        self.path = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    # TODO: add option to send telegram of this too
    def add_log(self, logType: str, message: str, sendPing: bool):
        msg = f"{logType}: {message}"

        #TODO: add to log file as well

        if sendPing:
            sendTelegram(msg)
