from typing import Type

from modules.logic.templates import LogType
from modules.login.login_route import fyers_model_class_obj as fyers
from datetime import datetime
from fyers_api.Websocket import ws
from threading import Thread
from modules.keys import app_credentials
from modules.logic.dateParsing import customDate
import datetime

from modules.logging.logging import loggerObject as logger


def getQuoteData(ticker: str):
    data = {
        'symbols': ticker
    }

    status, response = fyers.quotes(data)
    if status is True:
        try:
            cmd = response['d'][0]['v']['cmd']['c']
        except:
            cmd = response['d'][0]['v']['lp']
    else:
        return f"Error fetching quote data: {response}"

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
    _websocketThread = None

    def _onMessage(self, msg):
        logger.add_log(LogType.DEBUG, f"{self.ticker} {self.ltp}")
        self.ltp = float(msg[0]['ltp'])
        if self.time < float(msg[0]['timestamp']):
            self.time = float(msg[0]['timestamp'])

    ########################### THESE METHODS ARE EXPOSED ###########################

    def startWebsocket(self, logs):
        if self._websocketThread is not None:
            return self
        self._websocketThread = Thread(target=marketWebsocketMain,
                                       args=(self.ticker, self._onMessage, fyers.get_WS_Access_token(), logs,))
        logger.add_log(LogType.INFO, f'Starting websocket for {self.ticker}')
        self._websocketThread.start()
        return self

    def _getStrikePrice(self, method: str):
        if method.lower() == "closestvol":
            if self.ticker == "NSE:NIFTY50-INDEX" or self.ticker == "NSE:BANKNIFTY-INDEX":
                return int(self.ltp / 100) * 100 if self.ltp % 100 < 50 else (int(self.ltp / 100) + 1) * 100

        if method.lower() == "closestabsolute":
            if self.ticker == "NSE:NIFTY50-INDEX" or self.ticker == "NSE:BANKNIFTY-INDEX":
                lastTwo = self.ltp % 100
                if lastTwo <= 25:
                    return int(self.ltp / 100) * 100
                elif lastTwo < 75:
                    return (int(self.ltp / 100) * 100) + 50
                else:
                    return (int(self.ltp / 100) + 1) * 100

        return -1

    def getMonthlyExpiryAfterNDays(self, n: int, strike, opt_type: str):
        # Equity Options (Monthly Expiry)
        # {Ex}:{Ex_UnderlyingSymbol}{YY}{MMM}{Strike}{Opt_Type}
        # NSE:NIFTY20OCT11000CE

        dateObject = customDate()
        contract_month, year = dateObject.getExpiryMonthAfterNDays(n)

        underlying = self.ticker.split("-")[0]
        if underlying == "NSE:NIFTY50":
            underlying = "NSE:NIFTY"

        if type(strike) == str:
            strike = self._getStrikePrice(strike)

        contract = underlying + str(year)[2:] + contract_month.MMM + str(strike) + opt_type
        return contract

    def getWeeklyExpiryAfterNDays(self, n: int, strike, opt_type: str):
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

        if type(strike) == str:
            strike = self._getStrikePrice(strike)

        dd = str(date)
        if len(dd) == 1:
            dd = "0" + dd

        contract = underlying + str(year)[2:] + contract_month.M + dd + str(strike) + opt_type
        return contract

    def __init__(self, symbol: str, initWebsocket: bool):
        self.ticker: str = symbol
        self.ltp: float = getQuoteData(ticker=self.ticker)
        self.time: float = datetime.datetime.now().timestamp()

        if initWebsocket:
            self.startWebsocket(logger.logging_path)
