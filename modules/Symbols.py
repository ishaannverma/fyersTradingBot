from modules.singleSymbol import Symbol


class Symbols:
    _symbolsList = {

    }
    _logger = None
    _fyers = None
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
            symbolObject = Symbol(self._common_symbols[symbol], initWebsocket=True, fyers=self._fyers,
                                  logger=self._logger)
            self._symbolsList[self._common_symbols[symbol]] = symbolObject
        else:
            symbolObject = Symbol(symbol, initWebsocket=True, fyers=self._fyers, logger=self._logger)
            self._symbolsList[symbol] = symbolObject

        return symbolObject

    def remove(self, symbol: str):
        if symbol not in self._symbolsList:
            return

        del self._symbolsList[symbol]

    def __init__(self, fyers, logger):
        self._fyers = fyers
        self._logger = logger
