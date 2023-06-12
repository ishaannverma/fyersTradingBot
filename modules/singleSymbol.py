from typing import Type
from fyers_api import fyersModel
from datetime import datetime, timedelta
from fyers_api.Websocket import ws
from threading import Thread
from modules.keys import app_credentials


def getQuoteData(fyers: Type[type(fyersModel.FyersModel)], ticker: str):
    data = {
        'symbols': ticker
    }

    response = fyers.quotes(data)
    # pprint(response['d'][0])
    try:
        cmd = response['d'][0]['v']['cmd']['c']
    except:
        cmd = response['d'][0]['v']['lp']

    return cmd


def run_process_symbol_data(symbol, onMessage, access_token, logs):
    data_type = "symbolData"
    symbol = [symbol]
    fs = ws.FyersSocket(access_token=access_token, log_path=logs)
    fs.websocket_data = onMessage
    fs.subscribe(symbol=symbol, data_type=data_type)
    fs.keep_running()


def marketWebsocketMain(symbol, onMessage, WS_ACCESS_TOKEN, logs):
    run_process_symbol_data(symbol, onMessage, WS_ACCESS_TOKEN, logs)


class Symbol:
    ticker: str = ""
    ltp: float = ""
    time: float = ""
    _websocketThread = None

    def __init__(self, symbol: str, fyers):
        self.ticker: str = symbol
        self.ltp: float = getQuoteData(fyers=fyers, ticker=self.ticker)
        self.time: float = datetime.now().timestamp()

    def _onMessage(self, msg):
        print(msg)
        self.ltp = float(msg[0]['ltp'])
        self.time = datetime.fromtimestamp(msg[0]['timestamp'])

    def startWebsocket(self, logs):
        self._websocketThread = Thread(target=marketWebsocketMain,
                                       args=(self.ticker, self._onMessage, app_credentials['WS_ACCESS_TOKEN'], logs,))
        print(f'INFO: Starting websocket for {self.ticker}')
        self._websocketThread.start()
        return self


