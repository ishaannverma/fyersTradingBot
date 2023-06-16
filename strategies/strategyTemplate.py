import json
import os
import time
import uuid
from abc import ABC, abstractmethod
from threading import Thread

from modules.singleOrder import Order
from modules.templates import StrategyStatus, StrategyStatusValue, OrderSide
from typing import Type, List
from strategies.position import Position
from queue import Queue
from modules.logging import Logger
from modules.templates import LogType


class Strategy(ABC):
    strategyName: str = "Template"
    id: str = ""
    _status: Type[type(StrategyStatusValue)] = StrategyStatus.untraded
    paperTrade: bool = True

    _ordersQueue: Type[type(Queue)] = None
    _updatesQueue: Type[type(Queue)] = None
    _commandsQueue: Type[type(Queue)] = None

    positions: List[type(Position)] = []

    _killSwitch = False  # TODO use this
    _logger: Type[type(Logger)] = None
    _symbolsHandler = None

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
        # TODO change this behavior, this way position will never be 0
        while True:
            update = self._updatesQueue.get()
            # self._logger.add_log(LogType.DEBUG, update)
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
                self.positions.append(
                    Position(update['symbol'], update['qty'], OrderSide.fromSideInteger(update['side']),
                             update['avgPrice']))

    def placeOrder(self, order: Type[type(Order)]):
        order.strategyID = self.id
        if self.paperTrade:
            order.paperTrade = True
        self._ordersQueue.put(order)

    def save_json(self):
        data = self.get_snapshot_json()

        success = True
        with open(os.path.join(self._logger.strat_bin_path, f"{self.id}.json"), "w") as file:
            try:
                json.dump(data, file)
                self._logger.add_log(LogType.INFO, f"{self.strategyName} {self.id} successfully saved")
            except Exception as e:
                success = False
                self._logger.add_log(LogType.ERROR, f"{self.strategyName} {self.id} could not be saved: {e}")

        if not success:
            os.remove(os.path.join(self._logger.strat_bin_path, f"{self.id}.json"))

    @abstractmethod
    def _logic(self):
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
        Thread(target=self._logic).start()
        Thread(target=self._updatesQueueListener).start()
