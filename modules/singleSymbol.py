from typing import Type
from fyers_api import fyersModel
from datetime import datetime
from fyers_api.Websocket import ws
from threading import Thread
from modules.keys import app_credentials
from modules.dateParsing import customDate
import datetime

from modules.logging import Logger
from modules.templates import LogType


def getQuoteData(fyers: Type[type(fyersModel.FyersModel)], ticker: str):
    data = {
        'symbols': ticker
    }

    response = fyers.quotes(data)
    try:
        cmd = response['d'][0]['v']['cmd']['c']
    except:
        cmd = response['d'][0]['v']['lp']

    return cmd


########################### CODE TO RUN WEBSOCKET ###########################
def run_process_symbol_data(symbol, onMessage, access_token, logs):
    data_type = "symbolData"
    symbol = [symbol]
    fs = ws.FyersSocket(access_token=access_token, log_path=logs)
    fs.websocket_data = onMessage
    fs.subscribe(symbol=symbol, data_type=data_type)
    fs.keep_running()


def marketWebsocketMain(symbol, onMessage, WS_ACCESS_TOKEN, logs):
    run_process_symbol_data(symbol, onMessage, WS_ACCESS_TOKEN, logs)


########################### SINGLE SYMBOL CLASS ###########################
class Symbol:
    ticker: str = ""
    ltp: float = ""
    time: float = ""
    _logger: Type[type(Logger)] = None
    _websocketThread = None

    def _onMessage(self, msg):
        self.ltp = float(msg[0]['ltp'])
        if self.time < float(msg[0]['timestamp']):
            self.time = float(msg[0]['timestamp'])

    ########################### THESE METHODS ARE EXPOSED ###########################

    def startWebsocket(self, logs):
        if self._websocketThread is not None:
            return self
        self._websocketThread = Thread(target=marketWebsocketMain,
                                       args=(self.ticker, self._onMessage, app_credentials['WS_ACCESS_TOKEN'], logs,))
        # self._logger.add_log(LogType.INFO, f'Starting websocket for {self.ticker}')
        self._websocketThread.start()
        return self

    def getMonthlyExpiryAfterNDays(self, n: int, strike: int, opt_type: str):
        # Equity Options (Monthly Expiry)
        # {Ex}:{Ex_UnderlyingSymbol}{YY}{MMM}{Strike}{Opt_Type}
        # NSE:NIFTY20OCT11000CE

        dateObject = customDate()
        contract_month, year = dateObject.getExpiryMonthAfterNDays(n)

        underlying = self.ticker.split("-")[0]
        if underlying == "NSE:NIFTY50":
            underlying = "NSE:NIFTY"

        contract = underlying + str(year)[2:] + contract_month.MMM + str(strike) + opt_type
        return contract

    def getWeeklyExpiryAfterNDays(self, n: int, strike: int, opt_type: str):
        # Equity Options (Weekly Expiry)
        # {Ex}:{Ex_UnderlyingSymbol}{YY}{M}{dd}{Strike}{Opt_Type}
        # NSE:NIFTY20O0811000CE

        dateObject = customDate()
        date, contract_month, year = dateObject.getExpiryWeekAfterNDays(n)
        if dateObject.isLastThursday():
            return self.getMonthlyExpiryAfterNDays(n, strike, opt_type)

        underlying = self.ticker.split("-")[0]
        if underlying == "NSE:NIFTY50":
            underlying = "NSE:NIFTY"

        dd = str(date)
        if len(dd) == 1:
            dd = "0" + dd

        contract = underlying + str(year)[2:] + contract_month.M + dd + str(strike) + opt_type
        return contract

    def __init__(self, symbol: str, initWebsocket: bool, logger, fyers):
        self.ticker: str = symbol
        self.ltp: float = getQuoteData(fyers=fyers, ticker=self.ticker)
        self.time: float = datetime.datetime.now().timestamp()
        self ._logger = logger

        if initWebsocket:
            self.startWebsocket(self._logger.logging_path)
