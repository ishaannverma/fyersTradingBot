import os
import sys
from pprint import pprint

from modules.telegram import sendTelegram
from typing import Type
from modules.templates import LogTypeValue, LogType, LogLevel
import colorama
from colorama import Fore


class Logger:
    logging_path = ""
    strat_bin_path = ""
    _logLevel: int = LogLevel.ALL

    def __init__(self, logLevel):
        self._logLevel = logLevel

        self.logging_path = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(self.logging_path):
            os.mkdir(self.logging_path)

        self.strat_bin_path = os.path.join(os.getcwd(), 'strat_bin')
        if not os.path.exists(self.strat_bin_path):
            os.mkdir(self.strat_bin_path)

    # TODO: add option to send telegram of this too
    def add_log(self, logType: Type[type(LogTypeValue)], message: str, sendTelegramMessage: bool = False):
        msg = f"{logType.description}: {message}"

        if sendTelegramMessage or logType == LogType.UPDATE:
            sendTelegram(msg)

        if self._logLevel < logType.num:
            return

        if logType == LogType.FATAL:
            sys.exit(msg)
        elif logType == LogType.ERROR:
            print(Fore.RED + msg)
        elif logType == LogType.WARNING:
            print(Fore.YELLOW + msg)
        elif logType == LogType.INFO:
            print(Fore.BLUE + msg)
        elif logType == LogType.UPDATE:
            print(Fore.GREEN + msg)
        elif logType == LogType.DEBUG:
            print(Fore.RESET + msg)
        else:
            print(Fore.RESET + msg)
