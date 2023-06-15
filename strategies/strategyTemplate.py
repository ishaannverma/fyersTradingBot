import time
import uuid
from abc import ABC, abstractmethod
from threading import Thread

from modules.singleOrder import Order
from modules.templates import StrategyStatus, StrategyStatusValue, getOrderSideObjectForSideNum
from typing import Type, List
from strategies.position import Position
from queue import Queue
from modules.logging import Logger
from modules.templates import LogType


class Strategy(ABC):
    _status: Type[type(StrategyStatusValue)] = StrategyStatus.untraded
    _strategyName: str = "Template"
    id: str = ""
    _ordersQueue: Type[type(Queue)] = None
    _updatesQueue: Type[type(Queue)] = None
    _commandsQueue: Type[type(Queue)] = None
    positions: List[type(Position)] = []
    paperTrade: bool = True
    _killSwitch = False  # TODO use this
    _logger: Type[type(Logger)] = None
    ########################### USED BY STRATEGIES HANDLER ###########################

    def getPnL(self):
        pass

    def setQueues(self, orders, updates, commands):
        self._ordersQueue = orders
        self._updatesQueue = updates
        self._commandsQueue = commands

    ########################### USED OTHERWISE ###########################
    def _updatesQueueListener(self):
        # TODO WARNING: this will update position to the latest update of that symbol
        while True:
            update = self._updatesQueue.get()
            self._logger.add_log(LogType.DEBUG, update)
            found = False
            for position in self.positions:
                if position.ticker == update['symbol']:
                    position.quantity = update['qty']
                    position.avgPrice = update['avgPrice']
                    if found:
                        self._logger.add_log(LogType.WARNING,
                                             f"FOUND 2 INSTANCES OF SAME SYMBOL IN POSITION FOR STRATEGY {self.id}")
                    found = True

            if not found:
                self.positions.append(Position(update['symbol'], update['qty'], getOrderSideObjectForSideNum(update['side']), update['avgPrice']))

    def placeOrder(self, order: Type[type(Order)]):
        order.strategyID = self.id
        if self.paperTrade:
            order.paperTrade = True
        self._ordersQueue.put(order)

    @abstractmethod
    def _logic(self):
        pass

    @abstractmethod
    def save_binary(self):
        pass

    @abstractmethod
    def from_binary(self):
        pass

    def start(self):
        Thread(target=self._logic).start()
        Thread(target=self._updatesQueueListener).start()
