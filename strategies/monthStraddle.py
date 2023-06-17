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
        for ticker, position in self.positions.items():
            posDict = {
                'ticker': position.symbol.ticker,
                'qty': position.quantity,
                'avgPrice': position.avgPrice,
                'realized_pnl': position.realized_pnl
            }
            positions.append(posDict)

        data = {
            'strategyName': self.strategyName,
            'id': self.id,
            # 'status': self._status.description,
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
        time.sleep(2)
        symbol = self.underlying.getMonthlyExpiryAfterNDays(0, 17500, "PE")
        asset = self._symbolsHandler.get(symbol)
        order = Order(asset, 50, OrderSide.Buy, paperTrade=self.paperTrade)
        self.placeOrder(order)

        symbol = self.underlying.getMonthlyExpiryAfterNDays(0, 17500, "CE")
        asset = self._symbolsHandler.get(symbol)
        order = Order(asset, 50, OrderSide.Buy, paperTrade=self.paperTrade)
        self.placeOrder(order)

        time.sleep(10)

        while True:
            # real code starts from here
            if self._killSwitch:
                self.closeAllPositions()
                while len(self.positions) != 0:
                    time.sleep(5)
                    # TODO remove this: for now assuming this works - condition for closing
                    break
                # all positions now closed

                self._status: Type[type(StrategyStatusValue)] = StrategyStatus.closed
                self._logger.add_log(LogType.DEBUG, "Closed logic from strategy because killswitch")
                self.save_json()

                return

    def fill_from_json(self, jsonDict):
        self.id = jsonDict['id']
        self._killSwitch = jsonDict['killSwitch']

        # everything that's not in info has already been factored
        info = jsonDict['info']

        for position in info['positions']:
            posObject = Position(self._symbolsHandler.get(position['ticker']), position['qty'], position['avgPrice'], position['realized_pnl'])
            self.positions[posObject.symbol.ticker] = (posObject)

        self.underlying = self._symbolsHandler.get(info['underlyingTicker'])
        self.vix = self._symbolsHandler.get('indiavix')

        return self
