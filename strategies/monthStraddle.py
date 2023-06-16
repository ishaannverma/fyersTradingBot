import time
from threading import Thread
from uuid import uuid4
from typing import Type, List

from modules.Symbols import Symbols
from modules.singleOrder import Order
from strategies.position import Position
from strategies.strategyTemplate import Strategy
from modules.singleSymbol import Symbol
from modules.templates import OrderSide, LogType, StrategyStatus, StrategyStatusValue


class MonthStraddle(Strategy):
    strategyName: str = "MonthStraddle"
    id: str = uuid4().hex

    underlying: Type[type(Symbol)] = None
    vix: Type[type(Symbol)] = None

    def __init__(self, symbol: Type[type(Symbol)], vix: Type[type(Symbol)], fyers, symbolsHandler: Type[type(Symbols)],
                 logger, paperTrade=True):
        self._symbolsHandler = symbolsHandler
        self.underlying = symbol
        self.vix = vix
        self._fyers = fyers
        self._logger = logger
        self.paperTrade = paperTrade

    def getIntro(self, short: bool = True):
        reply = f"{self.id} {self.strategyName} for symbol = {self.underlying.ticker} with paperTrade = {self.paperTrade}"
        if short:
            return reply

    def get_snapshot_json(self):
        positions = []
        for position in self.positions:
            posDict = {
                'ticker': position.symbol.ticker,
                'qty': position.quantity,
                'side': position.side.symbolNum,
                'avgPrice': position.avgPrice,
            }
            positions.append(posDict)

        data = {
            'strategyName': self.strategyName,
            'id': self.id,
            'status': self._status.description,
            'paperTrade': self.paperTrade,
            'killSwitch': self._killSwitch,
            'info': {
                'positions': positions,
                'underlyingTicker': self.underlying.ticker
            }
        }
        return data

    def _logic(self):
        self._logger.add_log(LogType.INFO,
                             f"Starting logic for strategy {self.getIntro()}")
        # checking if it works
        time.sleep(5)
        symbol = self.underlying.getMonthlyExpiryAfterNDays(0, 17500, "PE")
        asset = self._symbolsHandler.get(symbol)
        order = Order(asset, 50, OrderSide.Buy)
        self.placeOrder(order)

        symbol = self.underlying.getMonthlyExpiryAfterNDays(0, 17500, "CE")
        asset = self._symbolsHandler.get(symbol)
        order = Order(asset, 50, OrderSide.Buy)
        self.placeOrder(order)

        time.sleep(10)
        self.save_json()

        while True:
            # real code starts from here
            if self._killSwitch:
                self.closeAllPositions()
                while len(self.positions) != 0:
                    time.sleep(5)
                    # TODO remove this: for now assuming this works
                    break
                # all positions now closed

                self._status: Type[type(StrategyStatusValue)] = StrategyStatus.closed
                self.save_json()

                return

    def fill_from_json(self, jsonDict):
        self.id = jsonDict['id']
        self._killSwitch = jsonDict['killSwitch']

        # everything that's not in info has already been factored
        info = jsonDict['info']

        for position in info['positions']:
            posObject = Position(self._symbolsHandler.get(position['ticker']), position['qty'], OrderSide.fromSideInteger(position['side']),
                                 position['avgPrice'])
            self.positions.append(posObject)

        self.underlying = self._symbolsHandler.get(info['underlyingTicker'])

        return self
