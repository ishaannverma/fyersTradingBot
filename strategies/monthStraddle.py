import time
from threading import Thread
from uuid import uuid4
from typing import Type, List

from modules.Symbols import Symbols
from modules.singleOrder import Order
from strategies.strategyTemplate import Strategy
from modules.singleSymbol import Symbol
from modules.templates import OrderSide


class MonthStraddle(Strategy):
    underlying: Type[type(Symbol)] = None
    vix: Type[type(Symbol)] = None
    _strategyName: str = "MonthStraddle"
    id: str = uuid4().hex

    def __init__(self, symbol: Type[type(Symbol)], vix: Type[type(Symbol)], fyers, symbolsHandler: Type[type(Symbols)], logger):
        self._symbolsHandler = symbolsHandler
        self.underlying = symbol
        self.vix = vix
        self._fyers = fyers
        self._logger = logger

    def start(self):
        Thread(target=self._updatesQueueListener).start()

    def _logic(self):
        # checking if it works
        time.sleep(5)
        symbol = self.underlying.getWeeklyExpiryAfterNDays(0, 17500, "PE")
        asset = self._symbolsHandler.get(symbol)
        order = Order(asset, 50, OrderSide.Buy)
        # self._ordersQueue.put(order)
        pass

    def _save_binary(self):
        pass

    def _get_binary(self):
        pass
