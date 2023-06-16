import json
import os
import time
import uuid
from abc import ABC, abstractmethod
from threading import Thread

from modules.singleOrder import Order
from modules.templates import StrategyStatus, StrategyStatusValue, OrderSide, OrderStatus
from typing import Type, List, Dict
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

    positions: Dict[str, type(Position)] = {}  # ticker to positions object
    _orders: Dict[str, List[type(Order)]] = {}  # ticker to orders

    _killSwitch = False  # TODO use this
    _logger: Type[type(Logger)] = None
    _symbolsHandler = None

    ########################### USED BY STRATEGIES HANDLER ###########################

    def getPnL(self):
        pnl = 0  # TODO keep pnl of closed positions too
        for ticker, position in self.positions.items():
            pnl += position.getPositionPnL()
        return pnl

    def setQueues(self, orders, updates, commands):
        self._ordersQueue = orders
        self._updatesQueue = updates
        self._commandsQueue = commands

    ########################### USED OTHERWISE ###########################
    def _updatesQueueListener(self):
        while True:
            if self._killSwitch:
                return

            order = self._updatesQueue.get()  # returns order object
            if order.status == OrderStatus.filled:
                if order.symbol.ticker in self.positions:
                    self.positions[order.symbol.ticker].addFilledOrder(order)
                else:
                    self.positions[order.symbol.ticker] = Position(order.symbol, order.filledQuantity, order.avgPrice)

    def _commandsQueueListener(self):
        while True:
            if self._killSwitch:
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

    def closeAllPositions(self):
        # close all positions
        # TODO cancel all orders
        for ticker, position in self.positions.items():
            asset = position.symbol
            order = Order(asset, position.orderedQuantity,
                          OrderSide.Buy if position.quantity < 0 else OrderSide.Sell, paperTrade=self.paperTrade)
            self.placeOrder(order)

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
        Thread(target=self._commandsQueueListener).start()
