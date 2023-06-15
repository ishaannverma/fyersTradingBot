import json
import os
import pickle
import time
from threading import Thread
from uuid import uuid4
from typing import Type, List

from modules.Symbols import Symbols
from modules.singleOrder import Order
from strategies.strategyTemplate import Strategy
from modules.singleSymbol import Symbol
from modules.templates import OrderSide, LogType


class MonthStraddle(Strategy):
    underlying: Type[type(Symbol)] = None
    vix: Type[type(Symbol)] = None
    _strategyName: str = "MonthStraddle"
    id: str = uuid4().hex

    def __init__(self, symbol: Type[type(Symbol)], vix: Type[type(Symbol)], fyers, symbolsHandler: Type[type(Symbols)],
                 logger, paperTrade=True):
        self._symbolsHandler = symbolsHandler
        self.underlying = symbol
        self.vix = vix
        self._fyers = fyers
        self._logger = logger
        self.paperTrade = paperTrade
        self._logger.add_log(LogType.INFO,
                             f"Starting strategy {self._strategyName} for symbol = {self.underlying.ticker} with paperTrade = {self.paperTrade}")

    def save_binary(self):
        positions = []
        for position in self.positions:
            posDict = {
                'ticker': position.ticker,
                'qty': position.quantity,
                'side': position.side.symbolNum,
                'avgPrice': position.avgPrice,
            }
            positions.append(posDict)

        data = {
            'strategyName': self._strategyName,
            'info': {
                'status': self._status.code,
                'paperTrade': self.paperTrade,
                'positions': positions,
                'underlyingTicker': self.underlying.ticker
            }
        }
        self._logger.add_log(LogType.DEBUG, data)

        success = True
        with open(os.path.join(self._logger.strat_bin_path, f"{self.id}.json"), "w") as file:
            try:
                json.dump(data, file)
                self._logger.add_log(LogType.INFO, f"{self._strategyName} {self.id} successfully saved")
            except Exception as e:
                success = False
                self._logger.add_log(LogType.ERROR, f"{self._strategyName} {self.id} could not be saved: {e}")

        if not success:
            os.remove(os.path.join(self._logger.strat_bin_path, f"{self.id}.json"))

    def _logic(self):
        # checking if it works
        time.sleep(5)
        symbol = self.underlying.getMonthlyExpiryAfterNDays(0, 17500, "PE")
        asset = self._symbolsHandler.get(symbol)
        order = Order(asset, 50, OrderSide.Buy)
        self.placeOrder(order)

        time.sleep(10)
        # self.save_binary()
        pass

    def from_binary(self):
        pass
