import time
from threading import Thread
from uuid import uuid4
from typing import Type, List

from modules.Symbols import Symbols
from modules.singleOrder import Order
from strategies.position import Position
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

    def get_snapshot_json(self):
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
            'id': self.id,
            'status': self._status.description,
            'paperTrade': self.paperTrade,
            'info': {
                'positions': positions,
                'underlyingTicker': self.underlying.ticker
            }
        }
        return data

    def _logic(self):
        self._logger.add_log(LogType.INFO,
                             f"Starting logic for strategy {self._strategyName} for symbol = {self.underlying.ticker} with paperTrade = {self.paperTrade}")
        # checking if it works
        time.sleep(5)
        symbol = self.underlying.getMonthlyExpiryAfterNDays(0, 17500, "PE")
        asset = self._symbolsHandler.get(symbol)
        order = Order(asset, 50, OrderSide.Buy)
        self.placeOrder(order)

        # time.sleep(10)
        # self.save_json()

    def fill_from_json(self, jsonDict):
        self.id = jsonDict['id']

        # everything that's not in info has already been factored
        info = jsonDict['info']

        for position in info['positions']:
            posObject = Position(position['ticker'], position['qty'], OrderSide.fromSideInteger(position['side']),
                                 position['avgPrice'])
            self.positions.append(posObject)

        self.underlying = self._symbolsHandler.get(info['underlyingTicker'])

        return self
