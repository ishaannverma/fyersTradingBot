import copy

from modules.strategies.singleSymbol import Symbol
from modules.login.login_route import fyers_model_class_obj as fyers
from modules.logging.logging import loggerObject

class Symbols:
    _symbolsList = {

    }
    _common_symbols = {
        'nifty50': "NSE:NIFTY50-INDEX",
        'indiavix': "NSE:INDIAVIX-INDEX",
        'banknifty': "NSE:BANKNIFTY-INDEX"
    }

    def get(self, symbol: str):
        if symbol in self._symbolsList:
            return self._symbolsList[symbol]
        if symbol in self._common_symbols and self._common_symbols[symbol] in self._symbolsList:
            return self._symbolsList[self._common_symbols[symbol]]

        if symbol in self._common_symbols:
            symbolObject = Symbol(self._common_symbols[symbol], initWebsocket=True)
            self._symbolsList[self._common_symbols[symbol]] = symbolObject
        else:
            symbolObject = Symbol(symbol, initWebsocket=True)
            self._symbolsList[symbol] = symbolObject

        return symbolObject

    def getAll(self):
        return self._symbolsList

    def remove(self, symbol: str):
        if symbol not in self._symbolsList:
            return

        del self._symbolsList[symbol]

    def __init__(self):
        pass
