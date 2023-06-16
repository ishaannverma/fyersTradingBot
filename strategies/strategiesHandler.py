import json
import os

from modules.templates import LogType, StrategyStatus
from strategies.monthStraddle import MonthStraddle
from strategies.strategyTemplate import Strategy
from typing import Type, Dict
from queue import Queue
from modules.orders import Orders


class StrategyHandler:
    strategies_dict: Dict[str, type(Strategy)] = {}
    _ordering_module = None
    _ordering_module_orders_queue = Queue()  # from strategy to ordering module
    _logger = None
    _fyers = None
    _symbolsHandler = None

    def loadSavedStrategies(self):
        for fileName in os.listdir(self._logger.strat_bin_path):
            if not fileName.endswith(".json"):
                continue

            with open(os.path.join(self._logger.strat_bin_path, fileName), "rb") as file:
                dataDict = json.load(file)
                strategyName = dataDict['strategyName']
                status = dataDict['status']
                paperTrade = dataDict['paperTrade']

                if status == StrategyStatus.closed.description:
                    continue

                self._logger.add_log(LogType.INFO, f"loading unclosed strategy {fileName.split('.')[0]}")

                if strategyName == "MonthStraddle":
                    strategyObject = MonthStraddle(None, None, self._fyers, self._symbolsHandler, self._logger,
                                                   paperTrade).fill_from_json(dataDict)
                    self.addStrategy(strategyObject)

                # self._logger.add_log(LogType.DEBUG, dataDict)

    def addStrategy(self, strategy: Type[type(Strategy)]):
        updatesQueue = Queue()  # from ordering module to strategy
        commandsQueue = Queue()  # from strategyHandler to strategy
        # TODO add commands queue to strategy too

        strategy.setQueues(self._ordering_module_orders_queue, updatesQueue, commandsQueue)

        strategyID = strategy.id

        self._ordering_module.addStrategy(strategyID, updatesQueue)
        if strategyID in self.strategies_dict:
            self._logger.add_log(LogType.ERROR, f"Trying to add strategy with ID {strategyID} when one already exists")
            return strategyID
        self.strategies_dict[strategyID] = strategy

        strategy.start()
        return strategyID

    def removeStrategy(self):
        pass

    def __init__(self, fyers, symbolsHandler, logger):
        self._fyers = fyers
        self._logger = logger
        self._ordering_module = Orders(self._ordering_module_orders_queue, self._fyers, self._logger)
        self._symbolsHandler = symbolsHandler

        self.loadSavedStrategies()
