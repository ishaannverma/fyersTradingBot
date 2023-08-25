import time
from uuid import uuid4
from typing import Type, Dict, List

from modules.strategies.Symbols import Symbols
from modules.logic.singleOrder import Order
from modules.strategies.position import Position
from modules.strategies.supported.strategyTemplate import Strategy
from modules.strategies.singleSymbol import Symbol
from modules.logic.templates import OrderSide, LogType, StrategyStatus, StrategyStatusValue
from modules.logging.logging import loggerObject as logger


class MonthStraddle(Strategy):

    def __init__(self, symbol: Type[type(Symbol)], vix: Type[type(Symbol)], symbolsHandler: Type[type(Symbols)],
                 paperTrade=True):
        self.strategyName: str = "MonthStraddle"
        self.id: str = uuid4().hex
        self.paperTrade = paperTrade

        self._symbolsHandler = symbolsHandler
        self.underlying = symbol
        self.vix = vix


        self.positions: Dict[str, type(Position)] = {}  # ticker to positions object
        self._orders: Dict[str, List[type(Order)]] = {}  # ticker to orders

        self._killSwitch = False  # TODO use this

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
        if not self.openPositionsExist():
            logger.add_log(LogType.INFO,
                           f"Starting logic for strategy {self.getIntro()}")
            # checking if it works
            time.sleep(2)
            symbol = self.underlying.getMonthlyExpiryAfterNDays(25, "closestabsolute", "PE")
            asset = self._symbolsHandler.get(symbol)
            order = Order(asset, 50, OrderSide.Sell, paperTrade=self.paperTrade)
            self.placeOrder(order)

            symbol = self.underlying.getMonthlyExpiryAfterNDays(25, "closestabsolute", "CE")
            asset = self._symbolsHandler.get(symbol)
            order = Order(asset, 50, OrderSide.Sell, paperTrade=self.paperTrade)
            self.placeOrder(order)

        # else: # if open positions exist

        time.sleep(10)

        while True:
            # real code starts from here
            if self._killSwitch:
                self.closeAllPositions()
                while len(self.positions) != 0:
                    time.sleep(50)
                    # TODO remove this: for now assuming this works - condition for closing
                    break
                # all positions now closed

                self._status: Type[type(StrategyStatusValue)] = StrategyStatus.closed
                logger.add_log(LogType.DEBUG, "Closed logic from strategy because killswitch")
                self.save_json()

                return

    def fill_from_json(self, jsonDict):
        self.id = jsonDict['id']
        self._killSwitch = jsonDict['killSwitch']

        # everything that's not in info has already been factored
        info = jsonDict['info']

        for position in info['positions']:
            posObject = Position(self._symbolsHandler.get(position['ticker']), position['qty'], position['avgPrice'],
                                 position['realized_pnl'])
            self.positions[posObject.symbol.ticker] = posObject

        self.underlying = self._symbolsHandler.get(info['underlyingTicker'])
        self.vix = self._symbolsHandler.get('indiavix')

        return self
