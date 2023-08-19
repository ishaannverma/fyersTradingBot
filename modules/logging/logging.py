import os
import sys

from typing import Type
from modules.logic.templates import LogType, LogLevel
from colorama import Fore


class Logger:
    logging_path = ""
    strat_bin_path = ""
    _logLevel: int = LogLevel.ALL

    def __init__(self, logLevel: Type[type(LogLevel)]):
        self._logLevel = logLevel

        self.logging_path = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(self.logging_path):
            os.mkdir(self.logging_path)

        self.strat_bin_path = os.path.join(os.getcwd(), 'strat_bin')
        if not os.path.exists(self.strat_bin_path):
            os.mkdir(self.strat_bin_path)

    # TODO: add option to send telegram of this too
    def add_log(self, logType: Type[type(LogType)], message: str):
        msg = f"{logType.description}: {message}"

        if self._logLevel < logType.num:
            return

        if logType == LogType.FATAL:
            sys.exit(msg)
        elif logType == LogType.ERROR:
            print(Fore.RED + msg + Fore.RESET)
        elif logType == LogType.WARNING:
            print(Fore.YELLOW + msg + Fore.RESET)
        elif logType == LogType.INFO:
            print(Fore.BLUE + msg + Fore.RESET)
        elif logType == LogType.UPDATE:
            print(Fore.GREEN + msg + Fore.RESET)
        elif logType == LogType.DEBUG:
            print(msg)
        else:
            print(msg)


loggerObject = Logger(LogLevel.DEBUG)
