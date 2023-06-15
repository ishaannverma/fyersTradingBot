import json
import os
import pickle

from modules.templates import LogType
from strategies.strategyTemplate import Strategy
from typing import Type
from queue import Queue
from modules.orders import Orders


class StrategyHandler:
    _strategies_list = []
    _ordering_module = None
    _ordering_module_orders_queue = Queue()  # from strategy to ordering module
    _logger = None
    _fyers = None

    def loadSaved(self):
        for fileName in os.listdir(self._logger.strat_bin_path):
            if not fileName.endswith(".json"):
                continue
            self._logger.add_log(LogType.INFO, f"loading unclosed strategy {fileName.split('.')[0]}")
            with open(os.path.join(self._logger.strat_bin_path, fileName), "rb") as file:
                dataDict = json.load(file)
                self._logger.add_log(LogType.DEBUG, dataDict)

    def __init__(self, fyers, logger):
        self._fyers = fyers
        self._logger = logger
        self._ordering_module = Orders(self._ordering_module_orders_queue, self._fyers, self._logger)
        self.loadSaved()

    def addStrategy(self, strategy: Type[type(Strategy)]):
        updatesQueue = Queue()  # from ordering module to strategy
        commandsQueue = Queue()  # from strategyHandler to strategy
        # TODO add commands queue to strategy too

        strategy.setQueues(self._ordering_module_orders_queue, updatesQueue, commandsQueue)

        strategyID = strategy.id

        self._ordering_module.addStrategy(strategyID, updatesQueue)
        self._strategies_list.append(strategy)

        strategy.start()
        return strategyID

    def removeStrategy(self):
        pass
