import time
import uuid
from abc import ABC, abstractmethod
from threading import Thread

from modules.singleOrder import Order
from modules.templates import StrategyStatus
from typing import Type, List
from strategies.position import Position
from queue import Queue


class Strategy(ABC):
    _status: Type[type(StrategyStatus)] = StrategyStatus()
    _strategyName: str = "Template"
    id: str = ""
    _ordersQueue: Type[type(Queue)] = None
    _updatesQueue: Type[type(Queue)] = None
    _commandsQueue: Type[type(Queue)] = None
    positions: List[type(Position)] = []
    paperTrade: bool = True
    _killSwitch = False  # TODO use this

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
            print(update)
            found = False
            for position in self.positions:
                if position.ticker == update['symbol']:
                    position.quantity = update['qty']
                    position.avgPrice = update['avgPrice']
                    if found:
                        print(f"WARNING: FOUND 2 INSTANCES OF SAME SYMBOL IN POSITION FOR STRATEGY {self.id}")
                    found = True

            if not found:
                self.positions.append(Position(update['symbol'], update['qty'], update['side'], update['avgPrice']))

    def placeOrder(self, order: Type[type(Order)]):
        order.strategyID = self.id
        if self.paperTrade:
            order.paperTrade = True
        self._ordersQueue.put(order)

    @abstractmethod
    def _logic(self):
        pass

    @abstractmethod
    def _save_binary(self):
        pass

    @abstractmethod
    def _get_binary(self):
        pass

    def start(self):
        Thread(target=self._logic).start()
        Thread(target=self._updatesQueueListener).start()
