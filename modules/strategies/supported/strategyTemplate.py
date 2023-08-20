import json
import os
import time
from abc import ABC, abstractmethod
from threading import Thread

from modules.logic.singleOrder import Order
from modules.logic.templates import OrderSide, OrderStatus, PositionStatus
from typing import Type, List, Dict
from modules.strategies.position import Position
from queue import Queue
from modules.logging.logging import loggerObject as logger
from modules.logic.templates import LogType


class Strategy(ABC):
    strategyName: str = "Template"
    id: str = ""
    # _status: Type[type(StrategyStatusValue)] = StrategyStatus.untraded
    paperTrade: bool = True

    _ordersQueue: Type[type(Queue)] = None
    _updatesQueue: Type[type(Queue)] = None
    _commandsQueue: Type[type(Queue)] = None

    positions: Dict[str, type(Position)] = {}  # ticker to positions object
    _orders: Dict[str, List[type(Order)]] = {}  # ticker to orders

    _killSwitch = False  # TODO use this
    _symbolsHandler = None

    ########################### USED BY STRATEGIES HANDLER ###########################

    def getPnL(self):
        realized = 0
        unrealized = 0
        pnl = 0  # TODO keep pnl of closed positions too
        for position in self.positions.values():
            realized += position.realized_pnl
            unrealized += position.getUnrealizedPnL()
        return realized, unrealized

    def setQueues(self, orders, updates, commands):
        self._ordersQueue = orders
        self._updatesQueue = updates
        self._commandsQueue = commands

    ########################### USED OTHERWISE ###########################
    def _updatesQueueListener(self):
        while True:
            if self._killSwitch:
                logger.add_log(LogType.DEBUG, "Closing updates queue from strategy because killswitch")
                return

            order = self._updatesQueue.get()  # returns order object
            if order.status == OrderStatus.filled:
                if order.symbol.ticker in self.positions:
                    self.positions[order.symbol.ticker].addFilledOrder(order)
                else:
                    self.positions[order.symbol.ticker] = Position(order.symbol, order.filledQuantity * order.side, order.avgPrice)

                self.save_json()

    def _commandsQueueListener(self):
        while True:
            if self._killSwitch:
                logger.add_log(LogType.DEBUG, "Closing commands queue from strategy because killswitch")
                return

            msg = self._commandsQueue.get()
            command = msg['command']
            if command == 'kill':
                self._killSwitch = True

    def placeOrder(self, order: Type[type(Order)]):
        order.strategyID = self.id
        if self.paperTrade:
            order.paperTrade = True
        self._ordersQueue.put(order)

        if order.symbol.ticker in self._orders:
            self._orders[order.symbol.ticker].append(order)
        else:
            self._orders[order.symbol.ticker] = [order]

    def openPositionsExist(self) -> bool:
        ans = False
        for ticker, position in self.positions.items():
            if position.position_status == PositionStatus.Open:
                ans = True
                break
        return ans

    def closeAllPositions(self):
        # close all positions
        time.sleep(3)  # wait for all orders in pipeline to get executed

        for ticker, position in self.positions.items():
            if position.position_status == PositionStatus.Closed:
                continue

            asset = position.symbol
            order = Order(asset, position.quantity, OrderSide.Buy if position.quantity < 0 else OrderSide.Sell,
                          paperTrade=self.paperTrade)
            self.placeOrder(order)

    def save_json(self):
        data = self.get_snapshot_json()

        success = True
        with open(os.path.join(logger.strat_bin_path, f"{self.id}.json"), "w") as file:
            try:
                json.dump(data, file)
                logger.add_log(LogType.INFO, f"{self.strategyName} {self.id} successfully saved")
            except Exception as e:
                success = False
                logger.add_log(LogType.ERROR, f"{self.strategyName} {self.id} could not be saved: {e}")

        if not success:
            os.remove(os.path.join(logger.strat_bin_path, f"{self.id}.json"))

    @abstractmethod
    def _logic(self):
        print("galt")
        pass

    @abstractmethod
    def getIntro(self, short: bool = True):
        pass

    @abstractmethod
    def get_snapshot_json(self):
        pass

    @abstractmethod
    def fill_from_json(self, jsonDict):
        pass

    def start(self):
        Thread(target=self._commandsQueueListener).start()
        Thread(target=self._updatesQueueListener).start()
        Thread(target=self._logic).start()
